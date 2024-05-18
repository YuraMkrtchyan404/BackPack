import sys
import logging
import toml
import subprocess
from .cronjob import setup_cron_job, get_cron_format
from .create_snapshot import setup_snapshot

#TODO here to understand why getpass not working properly

log_path = "/home/yura/capstone/BackPack/agent/log/agent.log"
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler(log_path),
                        logging.StreamHandler()
                    ])

config_path = "/home/yura/capstone/BackPack/agent/config.toml"

def load_config():
    with open(config_path, "r") as file:
        config = toml.load(file)
    return config

def cron_snap():
    if setup_snapshot():
        logging.info("Snapshot setup and backup completed successfully.")
        return True
    else:
        logging.error("Failed to set up snapshot.")
        return False

def get_python_path():
    try:
        result = subprocess.run(['which', 'python3'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return sys.executable
    except Exception as e:
        logging.error("Error fetching Python path: " + str(e))
        return sys.executable

if __name__ == "__main__":
    if cron_snap():
        config = load_config()
        backup_frequency = config.get('backup_frequency', 'daily')
        folder_name = config.get('folders')
        python_path = get_python_path()
        script_module = "src.cron_snapshot"
        command = f"sudo {python_path} -m {script_module}"
        try:
            cron_format = get_cron_format(backup_frequency)
            setup_cron_job(command, backup_frequency, folder_name)
        except ValueError as e:
            print(f"Error getting cron format: {e}")


#need to give the python_path explictly in order not repetition of cron jobs