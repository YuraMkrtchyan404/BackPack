from setup_snapshot import *

def main():
    if setup_snapshot():
        logging.info("Snapshot setup and backup completed successfully.")

if __name__ == "__main__":
    main()