import argparse
import getpass
import logging
import os
import toml
from . import grpc_handler

# Set up logging
user_name = getpass.getuser()
log_path = f"/home/{user_name}/capstone/BackPack/agent/log/agent.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_path),
        # logging.StreamHandler()  
    ]
)

config_path = f"/home/{user_name}/capstone/BackPack/agent/config.toml"

def load_config():
    try:
        with open(config_path, "r") as file:
            config = toml.load(file)
        logging.info("Configuration loaded successfully.")
        return config
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        raise

config = load_config()
server_ip = config.get("server_ip")
grpc_port = config.get("grpc_port")
standard_recovery_path = f"/home/{user_name}/recovered"

def recover_snap():
    try:
        parser = argparse.ArgumentParser(description="Recover a specific snapshot from the backup server")
        parser.add_argument('snapshot_name', type=str, help='The name of the snapshot to recover')
        parser.add_argument('mode', choices=['original', 'standard'], help='Recovery mode: "original" or "standard"')

        args = parser.parse_args()
        folder_name = args.snapshot_name.split('@')[0]

        logging.info(f"Snapshot name: {args.snapshot_name}")
        logging.info(f"Recovery mode: {args.mode}")

        if args.mode == "standard":
            recovery_folder = os.path.join(standard_recovery_path, folder_name)
            logging.info(f"Recovery folder: {recovery_folder}")
            if not os.path.exists(recovery_folder):
                os.makedirs(recovery_folder)
                logging.info(f"Created directory: {recovery_folder}")
            else:
                logging.info(f"Directory already exists: {recovery_folder}")

        grpc_handler.recover_snapshot(args.snapshot_name, args.mode, server_ip, grpc_port)
        logging.info("Snapshot recovery initiated successfully.")
    except Exception as e:
        logging.error(f"Failed to recover snapshot: {e}")
        raise

if __name__ == "__main__":
    recover_snap()
