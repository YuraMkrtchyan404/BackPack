import argparse
import toml
import grpc_handler

def load_config():
    with open("/home/yura/capstone/OS_Snapshots/agent/config.toml", "r") as file:
        config = toml.load(file)
    return config

config = load_config()
server_ip = config.get("server_ip")
grpc_port = config.get("grpc_port")

def main():
    parser = argparse.ArgumentParser(description='List snapshots from the backup server')
    parser.add_argument('--folder_name', type=str, help='Specify a folder name to list snapshots for that folder only', default='')
    args = parser.parse_args()
    
    snapshots = grpc_handler.request_snapshot_list_from_server(args.folder_name, server_ip, grpc_port)
    
    if snapshots:
        sorted_snapshots = sorted(snapshots, key=lambda x: x.split('@')[1], reverse=True)
        
        print("\nAvailable Snapshots:")
        print("-----------------------------")
        for snapshot in sorted_snapshots:
            print(snapshot)
    else:
        print("No snapshots available or failed to retrieve snapshots.")

if __name__ == "__main__":
    main()
