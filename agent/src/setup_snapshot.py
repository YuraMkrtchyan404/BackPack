import getpass
import subprocess
import os
import logging
import time
import toml
import socket
import json
import tempfile

from grpc_handler import notify_server_about_rsync_completion, notify_server_about_rsync_start

def load_config():
    with open("/home/yura/capstone/OS_Snapshots/agent/config.toml", "r") as file:
        config = toml.load(file)
    return config

config = load_config()
server_ip = config.get("server_ip")
server_username = config.get("server_username")
rsync_port = config.get("rsync_port")
grpc_port = config.get("grpc_port")
folders = config.get("folders")
standard_recovery_path = config.get("standard_recovery_path")
config_path = "/home/yura/capstone/OS_Snapshots/agent/config.toml"
ssh_password = config.get("ssh_password")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler("/home/yura/capstone/OS_Snapshots/agent/log/agent.log"),
                        logging.StreamHandler()
                    ])

def get_client_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # Does not actually send data
            return s.getsockname()[0]
    except Exception as e:
        logging.error(f"Failed to detect IP address: {e}")
        return "Unable to detect IP"

def insert_metadata_file(temp_dir, original_folder_path, standard_recovery_path):
    client_ip = get_client_ip()  
    client_username = getpass.getuser()
    metadata = {
        "original_path": original_folder_path,
        "standard_recovery_path": standard_recovery_path,
        "client_ip": client_ip,
        "client_username": client_username 
    }
    metadata_file_path = os.path.join(temp_dir, 'metadata.json')
    try:
        with open(metadata_file_path, 'w') as file:
            json.dump(metadata, file)
        logging.info(f"Metadata file created with IP and username at: {metadata_file_path}")
        return metadata_file_path
    except IOError as e:
        logging.error(f"Failed to write metadata file: {e}")
        raise

#TODO We should add permission to elioctl, mount and so on during the "make" process
#TODO something is off with absolute paths

def destroy_snapshot(minor, max_retries=15, retry_delay=5):
    retries = 0
    while retries < max_retries:
        destroy_cmd = ['elioctl', 'destroy', str(minor)]
        destroy_output = subprocess.run(destroy_cmd)
        
        if destroy_output.returncode == 0:
            logging.info(f"Snapshot {minor} successfully destroyed.")
            return True
        else:
            logging.error(f"Failed to destroy snapshot {minor}. Retrying...")
            retries += 1
            time.sleep(retry_delay)

    logging.error(f"Unable to destroy snapshot {minor} after {max_retries} retries.")
    return False

def get_block_device_for_folder(folder_path):
    abs_folder_path = os.path.abspath(folder_path)
    cmd = ['df', '-h', abs_folder_path]
    df_output = subprocess.run(cmd, capture_output=True, text=True)

    if df_output.returncode != 0:
        error_msg = "Error occurred while running df command."
        original_error = df_output.stderr
        logging.error(f"{error_msg}\n{original_error}")
        return None

    lines = df_output.stdout.strip().split('\n')

    if len(lines) > 1:
        columns = lines[1].split()
        if len(columns) > 0:
            return columns[0]

    logging.error("Block device not found for the specified folder")
    return None

def get_free_minor():
    minor_output = subprocess.run(['sudo', 'elioctl', 'get-free-minor'], capture_output=True, text=True)
    if minor_output.returncode != 0:
        original_error = minor_output.stderr
        logging.error(f"Error occurred while getting a free minor: {original_error}")
        return None

    minor = minor_output.stdout.strip()
    return minor

def mount_snapshot(snapshot_path, mount_point):
    snapshot_dir = os.path.join(mount_point, os.path.basename(snapshot_path))
    os.makedirs(snapshot_dir, exist_ok=True)
    mount_cmd = ['sudo', 'mount', snapshot_path, snapshot_dir]
    mount_output = subprocess.run(mount_cmd)
    if mount_output.returncode != 0:
        logging.error("Error occurred while mounting snapshot.")
        return False
    logging.info(f"Snapshot mounted successfully at {snapshot_dir}.")
    return True

def umount_snapshot(snapshot_path):
    umount_cmd = ['sudo', 'umount', snapshot_path]
    umount_output = subprocess.run(umount_cmd)
    if umount_output.returncode != 0:
        logging.error("Error occurred while umounting snapshot.")
        return False
    logging.info(f"Snapshot umounted successfully at {snapshot_path}.")
    return True

def full_path_of_mounted_folder(mount_point, snapshot_path, folder_path):
    abs_folder_path = os.path.abspath(folder_path)
    snapshot_dir = os.path.join(mount_point, os.path.basename(snapshot_path))
    mounted_folder_path = os.path.join(snapshot_dir, abs_folder_path.lstrip('/'))
    if os.path.exists(mounted_folder_path):
        logging.info("Full path of the mounted folder in snapshot: %s", mounted_folder_path)
        return mounted_folder_path
    else:
        logging.error("Folder not found in snapshot.")
        return None

def backup_to_server(mounted_folder_path, original_folder_path, standard_recovery_path):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            metadata_file_path = insert_metadata_file(temp_dir, original_folder_path, standard_recovery_path)
            logging.info("Metadata file prepared and stored temporarily.")

            folder_name = os.path.basename(mounted_folder_path)
            server_backup_dir = f"{server_username}@{server_ip}:/backup-pool/backup_data/{folder_name}"
            server_backup_data_dir = f"{server_backup_dir}/data/"
            server_backup_etc_dir = f"{server_backup_dir}/etc/"

            rsync_folder_cmd = ['sudo', 'sshpass', '-p', str(ssh_password), 'rsync', '-av', '-e', f'ssh -p {rsync_port}',
                                mounted_folder_path + '/', server_backup_data_dir]
            logging.info(f"Starting rsync for backup data to {server_backup_data_dir}")
            subprocess.run(rsync_folder_cmd, check=True)
            logging.info("Backup data rsync completed successfully.")

            rsync_metadata_cmd = ['sudo', 'sshpass', '-p', str(ssh_password), 'rsync', '-av', '-e', f'ssh -p {rsync_port}',
                                  metadata_file_path, server_backup_etc_dir]
            logging.info(f"Starting rsync for metadata file to {server_backup_etc_dir}")
            subprocess.run(rsync_metadata_cmd, check=True)
            logging.info("Metadata file rsync completed successfully.")

            rsync_config_cmd = ['sudo', 'sshpass', '-p', str(ssh_password), 'rsync', '-av', '-e', f'ssh -p {rsync_port}',
                                config_path, server_backup_etc_dir]
            logging.info(f"Starting rsync for configuration file to {server_backup_etc_dir}")
            subprocess.run(rsync_config_cmd, check=True)
            logging.info("Configuration file rsync completed successfully.")

            logging.info("Backup to server completed successfully.")
            return True
    except Exception as e:
        logging.error(f"Failed during backup operation: {e}")
        return False

def setup_snapshot():
    block_devices = set()  
    folder_mapping = {}

    for folder in folders:
        block_device = get_block_device_for_folder(folder)
        if block_device:
            block_devices.add(block_device)
            if block_device in folder_mapping:
                folder_mapping[block_device].append(folder)
            else:
                folder_mapping[block_device] = [folder]

    for block_device in block_devices:
        minor = get_free_minor()
        if not minor:
            return False
        
        device_folders = folder_mapping.get(block_device, [])

        folder_directory = os.path.dirname(os.path.abspath(device_folders[0])) if device_folders else ""

        if not folder_directory:
            folder_directory = "/var/OS_Snapshot/cow"
            os.makedirs(folder_directory, exist_ok=True)

        cow_file_path = os.path.join(folder_directory, f"cow_file{minor}")

        cmd = ['sudo', 'elioctl', 'setup-snapshot', block_device, cow_file_path, minor]
        setup_output = subprocess.run(cmd)
        
        if setup_output.returncode != 0:
            logging.error("Error occurred while creating snapshot.")
            return False

        snapshot_path = f"/dev/elastio-snap{minor}"
        mount_point = "/var/OS_Snapshot/data"
        
        if not mount_snapshot(snapshot_path, mount_point):
            destroy_snapshot(minor)
            return False

        for folder in device_folders:
            mounted_folder_path = full_path_of_mounted_folder(mount_point, snapshot_path, folder)
            if not mounted_folder_path:
                umount_snapshot(snapshot_path)
                destroy_snapshot(minor)
                return False
            notify_server_about_rsync_start(folder, server_ip, grpc_port)
            if not backup_to_server(mounted_folder_path, folder, standard_recovery_path):
                umount_snapshot(snapshot_path)
                destroy_snapshot(minor)
                return False
            notify_server_about_rsync_completion(folder, server_ip, grpc_port)
            
        umount_snapshot(snapshot_path)
        destroy_snapshot(minor)

    return True