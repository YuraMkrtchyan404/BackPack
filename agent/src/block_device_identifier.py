import subprocess
import os

def get_block_device_for_folder(folder_path):
    cmd = ['df', '-h', folder_path]
    df_output = subprocess.run(cmd, capture_output=True, text=True)

    lines = df_output.stdout.strip().split('\n')

    if len(lines) > 1:
        columns = lines[1].split()
        if len(columns) > 0:
            return columns[0]

    return None

def setup_snapshot(block_device, cow_file_path, minor):
    #minor can be find by running elioctl get-free-minor

    command = ['elioctl', 'setup-snapshot', block_device, cow_file_path, str(minor)]

    subprocess.run(command)


 # I need to identify the snapshot_device which will be in /dev/elastio-snap(minor)
def mount_snapshot(snapshot_device, mount_point):
    mount_cmd = ['mount', snapshot_device, mount_point]
    subprocess.run(mount_cmd)


def full_path_of_mounted_folder(mount_point, folder_path):
    mounted_folder_path = os.path.join(mount_point, folder_path.lstrip('/'))

    if os.path.exists(mounted_folder_path):
        print("Full path of the mounted folder in snapshot:", mounted_folder_path)
        return mounted_folder_path
    else:
        print("Error: Folder not found in snapshot.")

def backup_to_local(mounted_folder_path, backup_location):
    rsync_cmd = ['rsync', '-av', mounted_folder_path, backup_location]
    
    subprocess.run(rsync_cmd)

#reverting can be done by using rsync again with --delete, --inplace, --partial
#need to be careful with --inplace