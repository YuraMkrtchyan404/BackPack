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
    minor_output = subprocess.run(['sudo', 'elioctl', 'get-free-minor'], capture_output=True, text=True)
    if minor_output.returncode != 0:
        logging.error("Error occurred while getting a free minor.")
        return None

    minor = minor_output.stdout.strip()
    return minor

def mount_snapshot(snapshot_device, mount_point):
    snapshot_dir = os.path.join(mount_point, os.path.basename(snapshot_device))
    os.makedirs(snapshot_dir, exist_ok=True)

    mount_cmd = ['sudo', 'mount', snapshot_device, snapshot_dir]
    mount_output = subprocess.run(mount_cmd)

    if mount_output.returncode != 0:
        logging.error("Error occurred while mounting snapshot.")
        return False

    logging.info(f"Snapshot mounted successfully at {snapshot_dir}.")
    return True

def umount_snapshot(snapshot_device):

    umount_cmd = ['sudo', 'umount', snapshot_device]
    umount_output = subprocess.run(umount_cmd)

    if umount_output.returncode != 0:
        logging.error("Error occurred while umounting snapshot.")
        return False

    logging.info(f"Snapshot umounted successfully at {snapshot_device}.")
    return True

def full_path_of_mounted_folder(mount_point, snapshot_device, folder_path):
    snapshot_dir = os.path.join(mount_point, os.path.basename(snapshot_device))
    mounted_folder_path = os.path.join(snapshot_dir, folder_path.lstrip('/'))

    if os.path.exists(mounted_folder_path):
        logging.info("Full path of the mounted folder in snapshot: %s", mounted_folder_path)
        return mounted_folder_path
    else:
        logging.error("Folder not found in snapshot.")
        return None


# def backup_to_local(mounted_folder_path, backup_location):
#     rsync_cmd = ['sudo', 'rsync', '-anv', mounted_folder_path, backup_location]
#     rsync_output = subprocess.run(rsync_cmd)

#     if rsync_output.returncode != 0:
#         logging.error("Error occurred while backing up to local.")
#         return False

#     logging.info("Backup to local completed successfully.")
#     return True

def backup_to_server(mounted_folder_path, server_ip, server_username, server_port, zfs_backup_location):
    rsync_cmd = ['sudo', 'rsync', '-av', '-e', f'ssh -p {server_port}', mounted_folder_path, f'{server_username}@{server_ip}:{zfs_backup_location}']
    rsync_output = subprocess.run(rsync_cmd)
    
    print("rsync command: ", rsync_cmd)

    if rsync_output.returncode != 0:
        logging.error("Error occurred while backing up to the server.")
        return False

    logging.info("Backup to server completed successfully.")
    return True


def setup_snapshot(folder_path, server_ip, server_username, server_port, zfs_backup_location):
    block_device = get_block_device_for_folder(folder_path)
    if not block_device:
        return False

    minor = get_free_minor()
    if not minor:
        return False
    
    cow_directory = "/var/OS_Snapshot/cow"
    cow_file_path =  f"{cow_directory}/cow_file{minor}"
    
    cmd = ['sudo', 'elioctl', 'setup-snapshot', block_device, cow_file_path, minor]
    setup_output = subprocess.run(cmd)
    
    if setup_output.returncode != 0:
        logging.error("Error occurred while creating snapshot.")
        return False

    snapshot_device = f"/dev/elastio-snap{minor}"
    mount_point = "/var/OS_Snapshot/data"
    
    if not mount_snapshot(snapshot_device, mount_point):
        return False
    
    mounted_folder_path = full_path_of_mounted_folder(mount_point, snapshot_device, folder_path)
    if not mounted_folder_path:
        return False
    
    if not backup_to_server(mounted_folder_path, server_ip, server_username, server_port, zfs_backup_location):
        return False
    
    # Unmount the snapshot after backup
    umount_snapshot(snapshot_device)
    
    return True
