from concurrent import futures
import logging
import os
import subprocess
import grpc
from communication_pb2 import RsyncCompletionRequest, SnapshotCompletionResponse
from communication_pb2_grpc import RsyncNotificationsServicer, add_RsyncNotificationsServicer_to_server
from snapshot_history import create_snapshot
from os.path import basename

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler("../log/server.log"),
                        logging.StreamHandler()
                    ])

class RsyncNotificationsService(RsyncNotificationsServicer):
    def TakeSnapshotAfterRsyncCompletion(self, request, context):
        full_folder_path = request.folder_name
        folder_name = basename(full_folder_path)

        logging.info(f"Received rsync completion notification for folder '{folder_name}'")
        try:
            if create_snapshot(folder_name):
                logging.info(f"Snapshot created successfully for folder '{folder_name}'")

                return SnapshotCompletionResponse(success=True, message="Snapshot successfully added to the ZFS history on the server")
            else:
                raise Exception("Snapshot creation reported failure without exception.")
        except Exception as e:
            error_msg = f"Failed to create ZFS snapshot for folder '{folder_name}': {str(e)}"
            logging.error(error_msg, exc_info=True)
            return SnapshotCompletionResponse(success=False, message=error_msg)
    
    def PrepareDatasetBeforeRsyncStart(self, request, context):
        full_folder_path = request.folder_name
        folder_name = basename(full_folder_path)
        dataset_path = f"backup-pool/backup_data/{folder_name}"
        data_dataset_path = f"{dataset_path}/data"
        etc_dataset_path = f"{dataset_path}/etc"

        logging.info(f"Received rsync preparation notification for folder '{folder_name}'")
        try:
            # Check and create the main dataset if not exists
            result = subprocess.run(['sudo', 'zfs', 'list', dataset_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                subprocess.run(['sudo', 'zfs', 'create', dataset_path], check=True)
                logging.info(f"Dataset created successfully for folder '{folder_name}'")
            
            # Set ZFS permissions
            subprocess.run(['sudo', 'zfs', 'allow', 'user1808', 'create,mount,send,receive', dataset_path], check=True)
            logging.info(f"ZFS permissions set for user 'user1808' on '{dataset_path}'")

            # Process each sub-dataset (data and etc)
            for sub_dataset in [data_dataset_path, etc_dataset_path]:
                # Check and create sub-datasets if they do not exist
                result = subprocess.run(['sudo', 'zfs', 'list', sub_dataset], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode != 0:
                    subprocess.run(['sudo', 'zfs', 'create', sub_dataset], check=True)
                    logging.info(f"Child dataset '{sub_dataset}' created successfully")

                # Set ZFS and file system permissions
                subprocess.run(['sudo', 'zfs', 'allow', 'user1808', 'create,mount,send,receive', sub_dataset], check=True)
                subprocess.run(['sudo', 'chown', '-R', 'user1808:user1808', f"/{sub_dataset}"], check=True)
                subprocess.run(['sudo', 'chmod', '-R', 'u+rwX', f"/{sub_dataset}"], check=True)
                logging.info(f"Permissions configured for '{sub_dataset}'")

            return SnapshotCompletionResponse(success=True, message=f"Dataset {folder_name} prepared successfully")
        except Exception as e:
            error_msg = f"Failed to prepare dataset for folder '{folder_name}': {str(e)}"
            logging.error(error_msg, exc_info=True)
            return SnapshotCompletionResponse(success=False, message=error_msg)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    add_RsyncNotificationsServicer_to_server(RsyncNotificationsService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("gRPC server started. Listening on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
