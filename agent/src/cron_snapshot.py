import sys
from .cronjob import setup_cron_job
from .create_snapshot import setup_snapshot
from .setup_snapshot import *



def cron_snap():
    if setup_snapshot():
        logging.info("Snapshot setup and backup completed successfully.")
    else:
        logging.error("Failed to set up snapshot.")

if __name__ == "__main__":
    cron_snap()
    config = load_config()
    backup_frequency = config.get('backup_frequency', 'daily')
    script_path = 'src.cron_snapshot.py'
    command = f'sudo {sys.executable} -m {script_path}'
    setup_cron_job(command, backup_frequency)

#TODO the problem is that when running cmd with sudo getpass returns root and not working properly.