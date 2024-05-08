from concurrent import futures
import json
import logging
import subprocess
import grpc
from communication_pb2 import SnapshotCompletionResponse, ListSnapshotsResponse, RecoveryMode
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
    
    def PrepareDatasetBeforeRsyncStart(self, request, context):
        
        full_folder_path = request.folder_name
        folder_name = basename(full_folder_path)
        dataset_path = f"backup-pool/backup_data/{folder_name}"
        data_dataset_path = f"{dataset_path}/data"
        etc_dataset_path = f"{dataset_path}/etc"

        logging.info(f"Received rsync preparation notification for folder '{folder_name}'")
        try:
            result = subprocess.run(['sudo', 'zfs', 'list', dataset_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                subprocess.run(['sudo', 'zfs', 'create', dataset_path], check=True)
                logging.info(f"Dataset created successfully for folder '{folder_name}'")
            
            subprocess.run(['sudo', 'zfs', 'allow', 'user1808', 'create,mount,send,receive', dataset_path], check=True)
            logging.info(f"ZFS permissions set for user 'user1808' on '{dataset_path}'")

            for sub_dataset in [data_dataset_path, etc_dataset_path]:
                result = subprocess.run(['sudo', 'zfs', 'list', sub_dataset], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode != 0:
                    subprocess.run(['sudo', 'zfs', 'create', sub_dataset], check=True)
                    logging.info(f"Child dataset '{sub_dataset}' created successfully")

                subprocess.run(['sudo', 'zfs', 'allow', 'user1808', 'create,mount,send,receive', sub_dataset], check=True)
                subprocess.run(['sudo', 'chown', '-R', 'user1808:user1808', f"/{sub_dataset}"], check=True)
                subprocess.run(['sudo', 'chmod', '-R', 'u+rwX', f"/{sub_dataset}"], check=True)
                logging.info(f"Permissions configured for '{sub_dataset}'")

            return SnapshotCompletionResponse(success=True, message=f"Dataset {folder_name} prepared successfully")
        except Exception as e:
            error_msg = f"Failed to prepare dataset for folder '{folder_name}': {str(e)}"
            logging.error(error_msg, exc_info=True)
            return SnapshotCompletionResponse(success=False, message=error_msg)

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
        
    def ListSnapshots(self, request, context):
        
        folder_name = request.folder_name
        logging.info(f"Request to list snapshots for folder: '{folder_name}' (empty means all)")
        try:
            base_path = "backup-pool/backup_data"
            if folder_name:
                snapshot_search_command = ['sudo', 'zfs', 'list', '-t', 'snapshot', '-o', 'name', '-s', 'creation', '-r', f"{base_path}/{folder_name}"]
            else:
                snapshot_search_command = ['sudo', 'zfs', 'list', '-t', 'snapshot', '-o', 'name', '-s', 'creation', '-r', base_path]

            result = subprocess.run(snapshot_search_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                filtered_snapshots = [
                    snap.replace(f'{base_path}/', '') for snap in result.stdout.strip().split('\n')[1:]
                    if '@' in snap and not ('/etc@' in snap or '/data@' in snap)
                ]
                logging.info(f"Snapshots retrieved successfully: {filtered_snapshots}")
                return ListSnapshotsResponse(success=True, snapshots=filtered_snapshots, message="Snapshots listed successfully")
            else:
                error_msg = f"Error listing snapshots: {result.stderr.strip()}"
                logging.error(error_msg)
                return ListSnapshotsResponse(success=False, message=error_msg)
        except Exception as e:
            error_msg = f"Failed to list snapshots: {str(e)}"
            logging.error(error_msg, exc_info=True)
            return ListSnapshotsResponse(success=False, message=error_msg)
        
    def RecoverSnapshot(self, request, context):
        
        snapshot_name = request.snapshot_name
        recovery_mode = request.mode
        recovery_mode_name = RecoveryMode.Name(recovery_mode)
        logging.info(f"Received request to recover snapshot '{snapshot_name}' with mode {recovery_mode_name}")

        try:
            folder_name, snapshot_identifier = snapshot_name.split('@')
            dataset_path = f"/backup-pool/backup_data/{folder_name}"

            metadata = self.read_metadata(snapshot_name)

            if recovery_mode == RecoveryMode.ORIGINAL:
                target_directory = metadata['original_path']
            elif recovery_mode == RecoveryMode.STANDARD:
                target_directory = metadata['standard_recovery_path']
            else:
                raise ValueError("Invalid recovery mode specified")

            client_ip = metadata['client_ip']
            client_username = metadata['client_username']
            remote_target_directory = f"{client_username}@{client_ip}:{target_directory}"

            ssh_options = "-e 'ssh -p 22'"  # Define SSH options
            rsync_command = ['sudo', 'rsync', '-av', '--delete', ssh_options, f"{dataset_path}/data/.zfs/snapshot/{snapshot_identifier}/", remote_target_directory]
            result = subprocess.run(rsync_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if result.returncode == 0:
                logging.info(f"Snapshot '{snapshot_name}' recovered successfully to {target_directory} on remote client {client_ip}")
                return SnapshotCompletionResponse(success=True, message="Snapshot recovered successfully")
            else:
                raise subprocess.CalledProcessError(result.returncode, ' '.join(rsync_command), result.stderr)

        except Exception as e:
            error_msg = f"Failed to recover snapshot '{snapshot_name}': {str(e)}"
            logging.error(error_msg, exc_info=True)
            return SnapshotCompletionResponse(success=False, message=error_msg)

    def read_metadata(self, snapshot_name):

        try:
            # Assuming snapshot_name is formatted as 'folder_name@snapshot_identifier'
            folder_name, snapshot_identifier = snapshot_name.split('@')
            metadata_path = f"/backup-pool/backup_data/{folder_name}/etc/.zfs/snapshot/{snapshot_identifier}/metadata.json"

            with open(metadata_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from metadata file at {metadata_path}")
            raise
        except FileNotFoundError:
            logging.error(f"Metadata file not found at {metadata_path}")
            raise
        except Exception as e:
            logging.error(f"Failed to read metadata for snapshot '{snapshot_name}': {str(e)}")
            raise

def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    add_RsyncNotificationsServicer_to_server(RsyncNotificationsService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("gRPC server started. Listening on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
