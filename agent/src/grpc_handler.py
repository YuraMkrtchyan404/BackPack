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

# def is_port_open(host, port):
#     """Check if a port is open on the given host."""
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.settimeout(5)
#     try:
#         s.connect((host, port))
#         s.shutdown(socket.SHUT_RDWR)
#         return True
#     except socket.error as e:
#         logging.error(f"Port {port} on {host} is not reachable: {e}")
#         return False
#     finally:
#         s.close()

def notify_server_about_rsync_completion(folder, server_ip, grpc_port):
    # if not is_port_open(server_ip, grpc_port):
    #     logging.error(f"Cannot establish gRPC channel, port {grpc_port} is busy or not accessible.")
    #     return

    try:
        with grpc.insecure_channel(f'{server_ip}:{grpc_port}') as channel:
            logging.info(f"GRPC insecure channel established: {server_ip}:{grpc_port}")
            # print(1)
            stub = communication_pb2_grpc.RsyncNotificationsStub(channel)
            # print(2)
            request = communication_pb2.RsyncCompletionRequest(folder_name=folder)
            # print(3)
            response = stub.TakeSnapshotAfterRsyncCompletion(request)
            # print(4)
            if response.success:
                logging.info(response.message)
            else:
                logging.error(response.message)
    except grpc.RpcError as e:
        logging.error(f"gRPC call failed: {e.details()}")
        

# def notify_server_about_rsync_completion(folder, server_ip, port):
#     with grpc.insecure_channel(f'{server_ip}:{port}') as channel:
#         print(f'GRPC insecure channel: {server_ip}:{port}')
#         stub = communication_pb2_grpc.RsyncNotificationsStub(channel)
#         request = communication_pb2.RsyncCompletionRequest(folder_name=folder)
#         response = stub.TakeSnapshotAfterRsyncCompletion(request)
#         if response.success:
#             logging.info(str(response.message))
#         else:
#             logging.error(response.message)