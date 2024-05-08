import subprocess
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
    dataset_path = f"backup-pool/backup_data/{folder_name}"
    snapshot_name = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + folder_name

    try:
        subprocess.run(['sudo', 'zfs', 'snapshot', '-r', f'{dataset_path}@{snapshot_name}'], check=True)
        logging.info(f"Snapshot '{snapshot_name}' created for dataset '{dataset_path}'.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error creating snapshot '{snapshot_name}' for dataset '{dataset_path}': {e}")
        return False
