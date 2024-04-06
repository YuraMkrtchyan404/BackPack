from setup_snapshot import *
from utils import *

def main():
    #folder_path = "/home/aivanyan/capstone"
    
    folder_path = "/home/yura/capstone/test_folder"

    if setup_snapshot(folder_path, "5.77.254.92", "user1808", 9122, "/backup-pool/backup_data"):
        logging.info("Snapshot setup and backup completed successfully.")
    else:
        logging.error("Failed to setup snapshot and backup.")
    #destroy_snapshot(0)

if __name__ == "__main__":
    main()