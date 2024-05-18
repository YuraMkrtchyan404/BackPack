import subprocess
import os
import logging
from .grpc_handler import notify_server_about_rsync_completion, notify_server_about_rsync_start
from .setup_snapshot import *


user_name = getpass.getuser()
config_path = f"/home/yura/capstone/BackPack/agent/config.toml"
def load_config():
    with open(config_path, "r") as file:
        config = toml.load(file)
    return config

folders = config.get("folders")

def setup_snapshot():
    block_devices = set()
    folder_mapping = {}

    if not folders:
        logging.error("No folders provided for setup_snapshot.")
        return False
    
    for folder in folders:
        if not os.path.exists(folder):
            logging.error(f"Folder does not exist: {folder}")
            return False
        block_device = get_block_device_for_folder(folder)
        if block_device:
            block_devices.add(block_device)
            if block_device in folder_mapping:
                folder_mapping[block_device].append(folder)
            else:
                folder_mapping[block_device] = [folder]

    if not block_devices:
        logging.error("No valid block devices found for the folders.")
        return False
    
    for block_device in block_devices:
        minor = get_free_minor()
        if not minor:
            logging.error("Failed to obtain a free minor number for device mapping.")
            return False

        device_folders = folder_mapping.get(block_device, [])

        folder_directory = os.path.dirname(os.path.abspath(device_folders[0])) if device_folders else COW_DIR

        if not os.path.exists(folder_directory):
            try:
                os.makedirs(folder_directory, exist_ok=True)
            except PermissionError as e:
                logging.error(f"Permission denied when creating directory {folder_directory}: {str(e)}")
                return False

        cow_file_path = os.path.join(folder_directory, f"cow_file{minor}")
        cmd = ['sudo', 'elioctl', 'setup-snapshot', block_device, cow_file_path, minor]
        setup_output = subprocess.run(cmd, capture_output=True, text=True)

        if setup_output.returncode != 0:
            logging.error(f"Error occurred while creating snapshot: {setup_output.stderr}")
            return False

        snapshot_path = f"/dev/elastio-snap{minor}"
        mount_point = DATA_DIR

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