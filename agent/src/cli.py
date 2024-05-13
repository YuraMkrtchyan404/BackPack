import logging
import click
import toml
import getpass
import subprocess
import sys

user_name = getpass.getuser()
log_path = f"/home/{user_name}/capstone/OS_Snapshots/agent/log/agent.log"
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler(log_path),
                        logging.StreamHandler()
                    ])

config_path = f"/home/{user_name}/capstone/OS_Snapshots/agent/config.toml"

@click.group()
def backpack():
    pass

@backpack.command()
@click.argument('mode', type=click.Choice(['auto', 'manual'], case_sensitive=False))
def start(mode):
    try:
        with open(config_path, 'r') as config_file:
            config_data = toml.load(config_file)
    except FileNotFoundError:
        config_data = {}
        logging.error("No configuration file found, creating a new one.")
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        return

    folders_input = click.prompt("Folders")
    config_data['folders'] = [folder.strip() for folder in folders_input.split(',')]

    if mode == "auto":
        frequency = click.prompt("Backup Frequency")
        config_data['backup_frequency'] = frequency

    try:
        with open(config_path, 'w') as config_file:
            toml.dump(config_data, config_file)
        logging.info("Configuration updated successfully.")
    except Exception as e:
        logging.error(f"Failed to write configuration: {e}")

    if mode == "manual":
        from .create_snapshot import setup_snapshot
        if setup_snapshot():
            logging.info("Snapshot setup completed successfully.")
        else:
            logging.error("Failed to set up snapshot.")
    else:
        package_path = 'src.cron_snapshot'
        subprocess.run([sys.executable, '-m', package_path], check=True)

@backpack.command()
@click.argument('folder_name', required=False)
def list(folder_name=None):
    args = [sys.executable, "-m", "src.list_snapshots"]
    if folder_name:
        args.extend(['--folder_name', folder_name])
    try:
        subprocess.run(args, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to list snapshots: {e}")

@backpack.command()
@click.argument('snapshot_name')
@click.argument('mode', type=click.Choice(['original', 'standard'], case_sensitive=False))
def recover(snapshot_name, mode):
    module_name = "src.recover_snapshot"
    args = [sys.executable, "-m", module_name, snapshot_name, mode]
    try:
        subprocess.run(args, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to recover snapshot: {e}")

if __name__ == '__main__':
    backpack()
