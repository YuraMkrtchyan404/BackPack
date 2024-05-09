import getpass
import logging
import toml
import grpc
import communication_pb2
import communication_pb2_grpc
# os.environ['GRPC_VERBOSITY'] = 'DEBUG'
# os.environ['GRPC_TRACE'] = 'all'

user_name = getpass.getuser()
config_path = f"/home/{user_name}/capstone/OS_Snapshots/agent/config.toml"
def load_config():
    with open(config_path, "r") as file:
        config = toml.load(file)
    return config

config = load_config()
server_ip = config.get("server_ip")
grpc_port = config.get("grpc_port")

log_path = f"/home/{user_name}/capstone/OS_Snapshots/agent/log/agent.log"
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler(log_path),
                        logging.StreamHandler()
                    ])

def notify_server_about_rsync_start(folder, server_ip, grpc_port):
    try:
        with grpc.insecure_channel(f'{server_ip}:{grpc_port}') as channel:
            logging.info(f"GRPC insecure channel established: {server_ip}:{grpc_port}")
            stub = communication_pb2_grpc.RsyncNotificationsStub(channel)
            request = communication_pb2.RsyncStartRequest(folder_name=folder)
            response = stub.PrepareDatasetBeforeRsyncStart(request)
            if response.success:
                logging.info(response.message)
            else:
                logging.error(response.message)
    except grpc.RpcError as e:
        logging.error(f"gRPC call for rsync start preperation failed: {e.details()}")

def notify_server_about_rsync_completion(folder, server_ip, grpc_port):
    try:
        with grpc.insecure_channel(f'{server_ip}:{grpc_port}') as channel:
            logging.info(f"GRPC insecure channel established: {server_ip}:{grpc_port}")
            stub = communication_pb2_grpc.RsyncNotificationsStub(channel)
            request = communication_pb2.RsyncCompletionRequest(folder_name=folder)
            response = stub.TakeSnapshotAfterRsyncCompletion(request)
            if response.success:
                logging.info(response.message)
            else:
                logging.error(response.message)
    except grpc.RpcError as e:
        logging.error(f"gRPC call for taking a zfs snapshot failed: {e.details()}")
        
def request_snapshot_list_from_server(folder, server_ip, grpc_port):
    try:
        with grpc.insecure_channel(f'{server_ip}:{grpc_port}') as channel:
            logging.info(f"GRPC insecure channel established for listing snapshots: {server_ip}:{grpc_port}")
            stub = communication_pb2_grpc.RsyncNotificationsStub(channel)
            request = communication_pb2.ListSnapshotsRequest(folder_name=folder)
            response = stub.ListSnapshots(request)
            if response.success:
                logging.info(f"Successfully retrieved snapshot list: {response.snapshots}")
                return response.snapshots
            else:
                logging.error(f"Failed to retrieve snapshot list: {response.message}")
    except grpc.RpcError as e:
        logging.error(f"gRPC call for listing snapshots failed: {e.details()}")
        return None
    
def recover_snapshot(snapshot_name, recovery_mode, server_ip, grpc_port):
    try:
        with grpc.insecure_channel(f'{server_ip}:{grpc_port}') as channel:
            logging.info(f"GRPC insecure channel established for recovering a snapshot: {server_ip}:{grpc_port}")
            stub = communication_pb2_grpc.RsyncNotificationsStub(channel)
            mode = communication_pb2.ORIGINAL if recovery_mode == 'original' else communication_pb2.STANDARD
            request = communication_pb2.RecoverSnapshotRequest(snapshot_name=snapshot_name, mode=mode)
            response = stub.RecoverSnapshot(request)
            if response.success:
                logging.info(f"Snapshot recovery successful: {response.message}")
                return response.message
            else:
                logging.error(f"Snapshot recovery failed: {response.message}")
                return response.message
    except grpc.RpcError as e:
        logging.error(f"gRPC call for recovering snapshot failed: {e.details()}")
        return f"Failed to recover snapshot due to a gRPC error: {e.details()}"
