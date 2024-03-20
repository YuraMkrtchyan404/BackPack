import subprocess
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def get_block_device_for_folder(folder_path):
    cmd = ['df', '-h', folder_path]
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
    minor_output = subprocess.run(['elioctl', 'get-free-minor'], capture_output=True, text=True)
    if minor_output.returncode != 0:
        logging.error("Error occurred while getting a free minor.")
        return None

    minor = minor_output.stdout.strip()
    return minor

def mount_snapshot(snapshot_device, mount_point):
    mount_cmd = ['mount', snapshot_device, mount_point]
    mount_output = subprocess.run(mount_cmd)

    if mount_output.returncode != 0:
        logging.error("Error occurred while mounting snapshot.")
        return False

    logging.info("Snapshot mounted successfully.")
    return True

def full_path_of_mounted_folder(mount_point, folder_path):
    mounted_folder_path = os.path.join(mount_point, folder_path.lstrip('/'))

    if os.path.exists(mounted_folder_path):
        logging.info("Full path of the mounted folder in snapshot: %s", mounted_folder_path)
        return mounted_folder_path
    else:
        logging.error("Folder not found in snapshot.")
        return None

def backup_to_local(mounted_folder_path, backup_location):
    rsync_cmd = ['rsync', '-av', mounted_folder_path, backup_location]
    rsync_output = subprocess.run(rsync_cmd)

    if rsync_output.returncode != 0:
        logging.error("Error occurred while backing up to local.")
        return False

    logging.info("Backup to local completed successfully.")
    return True

def setup_snapshot(folder_path, cow_file_path):
    block_device = get_block_device_for_folder(folder_path)
    if not block_device:
        return False

    minor = get_free_minor()
    if not minor:
        return False
    
    cmd = ['elioctl', 'setup-snapshot', block_device, cow_file_path, minor]
    setup_output = subprocess.run(cmd)
    
    if setup_output.returncode != 0:
        logging.error("Error occurred while creating snapshot.")
        return False

    snapshot_device = f"/dev/elastio-snap{minor}"
    mount_point = "/home/aivanyan/OS_capstone/OS_Snapshots/mnt"
    
    if not mount_snapshot(snapshot_device, mount_point):
        return False
    
    mounted_folder_path = full_path_of_mounted_folder(mount_point, folder_path)
    if not mounted_folder_path:
        return False
    
    backup_location = "/home/aivanyan/OS_capstone/OS_Snapshots/backup"
    if not backup_to_local(mounted_folder_path, backup_location):
        return False
    
    return True

