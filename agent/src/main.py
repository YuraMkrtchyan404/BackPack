from setup_snapshot import *

def main():
    folder_path = "/home/aivanyan/capstone"
    cow_file_path = "/.elastio"

    if setup_snapshot(folder_path, cow_file_path):
        logging.info("Snapshot setup and backup completed successfully.")
    else:
        logging.error("Failed to setup snapshot and backup.")

if __name__ == "__main__":
    main()