from setup_snapshot import *
from cronjob import *

def main():
    if setup_snapshot():
       logging.info("Snapshot setup and backup completed successfully.")
        

if __name__ == "__main__":
    main()
    config = load_config()
    backup_frequency = config.get('backup_frequency', 'daily')
    setup_cron_job('sudo /home/yura/capstone/OS_Snapshots/agent/agentenv/bin/python3 /home/yura/capstone/OS_Snapshots/agent/src/main.py', backup_frequency)