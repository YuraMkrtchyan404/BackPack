import argparse
import getpass
import toml
import grpc_handler

user_name = getpass.getuser()
config_path = f"/home/{user_name}/capstone/OS_Snapshots/agent/config.toml"
def load_config():
    with open(config_path, "r") as file:
        config = toml.load(file)
    return config

config = load_config()
server_ip = config.get("server_ip")
grpc_port = config.get("grpc_port")

def main():
    parser = argparse.ArgumentParser(description="Recover a specific snapshot from the backup server")
    parser.add_argument('snapshot_name', type=str, help='The name of the snapshot to recover')
    parser.add_argument('mode', choices=['original', 'standard'], help='Recovery mode: "original" or "standard"')

    args = parser.parse_args()

    grpc_handler.recover_snapshot(args.snapshot_name, args.mode, server_ip, grpc_port)
if __name__ == "__main__":
    main()
