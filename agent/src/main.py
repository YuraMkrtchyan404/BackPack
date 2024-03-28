from setup_snapshot import *
from utils import *

def main():
    #folder_path = "/home/aivanyan/capstone"
    

    folder_path = "/home/aivanyan/test_file"

    if setup_snapshot(folder_path):
        logging.info("Snapshot setup and backup completed successfully.")
    else:
        logging.error("Failed to setup snapshot and backup.")
    #destroy_snapshot(0)

if __name__ == "__main__":
    main()