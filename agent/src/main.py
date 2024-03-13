from block_device_identifier import get_block_device_for_folder

def main():
    folder_path = "/home/aivanyan/capstone"
    block_device = get_block_device_for_folder(folder_path)

    if block_device:  
        print("Block device for folder:", block_device)
    else:
        print("Error: Block device not found for the specified folder.")

if __name__ == "__main__":
    main()
