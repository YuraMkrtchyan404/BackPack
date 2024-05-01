import subprocess
import json
import os
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler("../log/server.log"), 
                        logging.StreamHandler()
                    ])

# TODO Send config with every backup. Retrieve these from the config file. 
backup_image_root = "/backup-pool/backup_data"
snapshot_root = "backup-pool/snapshot_history"
server_username = "user1808"
server_ip = "5.77.254.92"
rsync_port = 9122  

def extract_original_folder_name(snapshot_name):
    try:
        part_after_at = snapshot_name.split('@')[1]
        original_folder_name = part_after_at.split('_')[1]
        return original_folder_name
    except IndexError as e:
        logging.error(f"Error extracting folder name from snapshot: {snapshot_name}, error: {e}")
        return None
    
def recover_snapshot(snapshot_name, client_ip, use_original_path=False):
    clone_name = f"{snapshot_name}-clone"
    original_folder_name = extract_original_folder_name(snapshot_name)
    logging.info(f"Attempting to clone snapshot {snapshot_name} to {clone_name}")

    try:
        subprocess.run(["sudo", "zfs", "clone", f"{snapshot_root}/{snapshot_name}", f"{snapshot_root}/{clone_name}"], check=True)
        logging.info(f"Snapshot cloned successfully: {clone_name}")

        mount_point = f"/mnt/{clone_name}"
        os.makedirs(mount_point, exist_ok=True)
        subprocess.run(["sudo", "mount", "-o", "zfs", f"{snapshot_root}/{clone_name}", mount_point], check=True)
        logging.info(f"Snapshot mounted at {mount_point}")

        # Read metadata to determine the recovery path
        metadata_path = os.path.join(backup_image_root, original_folder_name, 'metadata.json')
        with open(metadata_path, 'r') as file:
            metadata = json.load(file)
        
        if use_original_path:
            recovery_path = metadata['original_path']
        else:
            recovery_path = metadata['standart_recovery_path']
        
        logging.info(f"Recovering data to {recovery_path}")

        # Use rsync to transfer the snapshot data to the client's specified recovery path
        rsync_cmd = [
            'sudo', 'rsync', '-avz', '-e', f"ssh -p {rsync_port}",
            f"{mount_point}/", f"{server_username}@{client_ip}:{recovery_path}"
        ]
        subprocess.run(rsync_cmd, check=True)
        logging.info("Recovery completed successfully. Data transferred to client.")

    except subprocess.CalledProcessError as e:
        logging.error(f"An error occurred during processing: {e}")
    finally:
        # Cleanup: Unmount and destroy the clone
        try:
            subprocess.run(["sudo", "umount", mount_point], check=True)
            subprocess.run(["sudo", "zfs", "destroy", f"{snapshot_root}/{clone_name}"], check=True)
            logging.info("Cleanup completed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed during cleanup: {e}")
            