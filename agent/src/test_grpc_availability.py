import grpc
from communication_pb2_grpc import RsyncNotificationsStub

def check_grpc_connection(server_ip, port):
    """Attempt to establish a gRPC connection to the server and send a simple request."""
    channel = grpc.insecure_channel(f"{server_ip}:{port}")
    try:
        # Timeout needs to be specified to avoid hanging indefinitely if server doesn't respond
        grpc.channel_ready_future(channel).result(timeout=10)
        stub = RsyncNotificationsStub(channel)
        # Here, you would call one of the methods defined in your gRPC service
        # For example, suppose there's a method called StatusCheck that expects a StatusRequest
        # and returns a StatusResponse
        # response = stub.StatusCheck(communication_pb2.StatusRequest())
        # print(f"Received response: {response}")
        print("Successfully connected to gRPC server!")
    except grpc.RpcError as e:
        print(f"Failed to connect or communicate with gRPC server: {str(e)}")
    finally:
        channel.close()

if __name__ == "__main__":
    server_ip = "5.77.254.92"  # Replace with your server's IP address
    port = 8080  # The port your gRPC server is listening on
    check_grpc_connection(server_ip, port)