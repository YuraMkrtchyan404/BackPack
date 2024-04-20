from concurrent import futures
import logging
import grpc
from communication_pb2 import RsyncCompletionRequest, SnapshotCompletionResponse
from communication_pb2_grpc import RsyncNotificationsServicer, add_RsyncNotificationsServicer_to_server
from snapshot_history import create_snapshot

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler("../log/server.log"),
                        logging.StreamHandler()
                    ])

class RsyncNotificationsService(RsyncNotificationsServicer):
    def TakeSnapshotAfterRsyncCompletion(self, request, context):
        folder_name = request.folder_name
        logging.info(f"Received rsync completion notification for folder '{folder_name}'")
        try:
            create_snapshot(folder_name)
            logging.info(f"Snapshot created successfully for folder '{folder_name}'")
            return SnapshotCompletionResponse(success=True, message="Snapshot successfully added to the history")
        except Exception as e:
            error_msg = f"Failed to create snapshot for folder '{folder_name}': {str(e)}"
            logging.error(error_msg, exc_info=True)
            return SnapshotCompletionResponse(success=False, message=error_msg)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    add_RsyncNotificationsServicer_to_server(RsyncNotificationsService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    logging.info("Server started. Listening on port 50052.")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
