import subprocess

def get_block_device_for_folder(folder_path):
    # Run the df -h command with the specified folder path
    cmd = ['df', '-h', folder_path]
    df_output = subprocess.run(cmd, capture_output=True, text=True)

    # Split the output into lines
    lines = df_output.stdout.strip().split('\n')

    # Extract the block device name from the first line
    if len(lines) > 1:
        columns = lines[1].split()
        if len(columns) > 0:
            return columns[0]

    # If no filesystem name found, return None
    return None
