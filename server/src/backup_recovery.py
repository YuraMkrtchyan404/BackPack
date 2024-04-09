import subprocess
from datetime import datetime
import logging
logging.basicConfig(filename="/var/os_snapshot/server.log", level=logging.INFO, format='%(levelname)s: %(message)s')

def create_snapshot(backup_folder):
    # Get the current DateTime
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")

    # Snapshot name format: YYYYMMDDHHMMSS_backup_folder
    snapshot_name = f"{current_datetime}_{backup_folder}"

    # ZFS command to create a snapshot
    zfs_command = ['sudo', 'zfs', 'snapshot', f'/backup_pool/snapshot_history@{snapshot_name}']

    # Execute the ZFS command
    try:
        subprocess.run(zfs_command, check=True)
        logging.info(f"Snapshot created: {snapshot_name}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error: Failed to create snapshot - {e}")
        return False