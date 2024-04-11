import subprocess
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler("../log/server.log"),
                        logging.StreamHandler()
                    ])

def create_snapshot(folder_name):
    # Define paths
    snapshot_history_zfs_path = f"backup-pool/snapshot_history/{folder_name}"

    # Check if the folder exists in snapshot history dataset
    if not os.path.exists(f"/{snapshot_history_zfs_path}"):
        # Create the folder dataset in snapshot history
        try:
            subprocess.run(['sudo', 'zfs', 'create', snapshot_history_zfs_path], check=True)
            logging.info(f"Created dataset for folder '{folder_name}' in snapshot history.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error creating dataset for folder '{folder_name}' in snapshot history: {e}")
            return False

    # Get current datetime for snapshot name
    snapshot_name = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + folder_name

    # Create ZFS snapshot
    try:
        subprocess.run(['sudo', 'zfs', 'snapshot', f'{snapshot_history_zfs_path}@{snapshot_name}'], check=True)
        logging.info(f"Snapshot '{snapshot_name}' created for folder '{folder_name}'.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error creating snapshot '{snapshot_name}' for folder '{folder_name}': {e}")
        return False