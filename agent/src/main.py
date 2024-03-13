from block_device_identifier import *

def main():
    folder_path = "/home/aivanyan/capstone"
    block_device = get_block_device_for_folder(folder_path)

    if block_device:  
        print("Block device for folder:", block_device)
    else:
        print("Error: Block device not found for the specified folder.")

    #creating snapshot
    cow_file_path = "/.elastio"
    minor = 0
    setup_snapshot(block_device, cow_file_path, minor)
    #mounting snapshot 
    snapshot_device = "/dev/elastio-snap0"
    mount_point = "/home/aivanyan/OS_capstone/OS_Snapshots/mnt"
    mount_snapshot(snapshot_device, mount_point)
    #find the folder in the mounted point
    mounted_folder_path = full_path_of_mounted_folder(mount_point, folder_path)
    backup_location = "/home/aivanyan/OS_capstone/OS_Snapshots/backup"
    backup_to_local(mounted_folder_path, backup_location)
if __name__ == "__main__":
    main()
