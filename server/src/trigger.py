import os
import time
import logging
import traceback
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from snapshot_history import create_snapshot

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler("../log/server.log"),
                        logging.StreamHandler()
                    ])

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory and event.src_path.startswith('/backup-pool/backup_data/'):
            # Extract the subdirectory name
            relative_path = os.path.relpath(event.src_path, '/backup-pool/backup_data')
            folder_name = relative_path.split(os.path.sep)[0]
            if create_snapshot(folder_name):
                logging.info(f"Snapshot created for folder '{folder_name}'.")
            else:
                error_msg = f"Failed to create snapshot for folder '{folder_name}'."
                # Get the original error message
                original_error = traceback.format_exc()
                logging.error(f"{error_msg}\n{original_error}")

def watch_backup_data():
    observer = Observer()
    observer.schedule(MyHandler(), path="/backup-pool/backup_data", recursive=True)
    observer.start()
    logging.info("Watching /backup-pool/backup_data for changes...")
    try:
        while True:
            time.sleep(30)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    watch_backup_data()