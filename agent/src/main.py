from setup_snapshot import *

def main():
    #folder_path = "/home/aivanyan/capstone"
    
    folder_path = "/home/yura/capstone/test_folder"

    if setup_snapshot():
        logging.info("Snapshot setup and backup completed successfully.")

if __name__ == "__main__":
    main()