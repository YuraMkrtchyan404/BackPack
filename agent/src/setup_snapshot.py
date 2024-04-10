import subprocess
import os
import logging
import time
import toml
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler("agent/log/agent.log"),
                        logging.StreamHandler()
                    ])

#TODO We should add permission to elioctl, mount and so on during the "make" process

def load_config():
    with open("agent/config.toml", "r") as file:
        config = toml.load(file)
    return config

def destroy_snapshot(minor, max_retries=15, retry_delay=5):
    retries = 0
    while retries < max_retries:
        destroy_cmd = ['elioctl', 'destroy', str(minor)]
        destroy_output = subprocess.run(destroy_cmd)
        
        if destroy_output.returncode == 0:
            print(f"Snapshot {minor} successfully destroyed.")
            return True
        else:
            print(f"Failed to destroy snapshot {minor}. Retrying...")
            retries += 1
            time.sleep(retry_delay)

    print(f"Unable to destroy snapshot {minor} after {max_retries} retries.")
    return False

def get_block_device_for_folder(folder_path):
    abs_folder_path = os.path.abspath(folder_path)
    cmd = ['df', '-h', abs_folder_path]
    df_output = subprocess.run(cmd, capture_output=True, text=True)

    if df_output.returncode != 0:
        logging.error("Error occurred while running df command.")
        return None

    lines = df_output.stdout.strip().split('\n')

    if len(lines) > 1:
        columns = lines[1].split()
        if len(columns) > 0:
            return columns[0]

    logging.error("Block device not found for the specified folder.")
    return None

def get_free_minor():
    minor_output = subprocess.run(['sudo', 'elioctl', 'get-free-minor'], capture_output=True, text=True)
    if minor_output.returncode != 0:
        logging.error("Error occurred while getting a free minor.")
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

def backup_to_server(mounted_folder_path):
    config = load_config()
    server_ip = config.get("server_ip")
    server_username = config.get("server_username")
    port = config.get("port")

    rsync_cmd = ['sudo', 'rsync', '-av', '-e', f'ssh -p {port}', mounted_folder_path, f'{server_username}@{server_ip}:/backup-pool/backup_data']
    rsync_output = subprocess.run(rsync_cmd)

    if rsync_output.returncode != 0:
        logging.error("Error occurred while backing up to the server.")
        return False

    logging.info("Backup to server completed successfully.")
    return True


def setup_snapshot():
    config = load_config()
    folder_path = config.get("folders")[0]  #TODO multiple folder selection
    block_device = get_block_device_for_folder(folder_path)
    if not block_device:
        return False
    minor = get_free_minor()
    if not minor:
        return False
    
    folder_directory = os.path.dirname(os.path.abspath(folder_path))
    
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
    
    mounted_folder_path = full_path_of_mounted_folder(mount_point, snapshot_path, folder_path)
    if not mounted_folder_path:
        return False
    
    if not backup_to_server(mounted_folder_path):
        umount_snapshot(snapshot_path)
        destroy_snapshot(minor)
        return False
    
    umount_snapshot(snapshot_path)
    destroy_snapshot(minor)

    return True
