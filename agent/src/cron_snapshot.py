import os
import sys
import getpass
from .cronjob import setup_cron_job
from .create_snapshot import setup_snapshot
from .setup_snapshot import *



def cron_snap():
    config = load_config()
    if config is None:
        return
    
    backup_frequency = config.get('backup_frequency', 'daily')
    if setup_snapshot():
        logging.info("Snapshot setup and backup completed successfully.")
        script_path = 'src.cron_snapshot.py'
        command = f'sudo {sys.executable} {script_path}'
        setup_cron_job(command, backup_frequency)
    else:
        logging.error("Failed to set up snapshot.")

if __name__ == "__main__":
    cron_snap()
