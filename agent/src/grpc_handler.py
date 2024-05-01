import logging
import socket
import toml
import grpc
import communication_pb2
import communication_pb2_grpc
import os
# os.environ['GRPC_VERBOSITY'] = 'DEBUG'
# os.environ['GRPC_TRACE'] = 'all'

def load_config():
    with open("/home/yura/capstone/OS_Snapshots/agent/config.toml", "r") as file:
        config = toml.load(file)
    return config

config = load_config()
server_ip = config.get("server_ip")
grpc_port = config.get("grpc_port")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler("/home/yura/capstone/OS_Snapshots/agent/log/agent.log"),
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