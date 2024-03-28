import subprocess
import time

def destroy_snapshot(minor, max_retries=15, retry_delay=5):
    retries = 0
    while retries < max_retries:
        destroy_cmd = ['elioctl', 'destroy', str(minor)]
        destroy_output = subprocess.run(destroy_cmd)
        
        if destroy_output.returncode == 0:
            print(f"Snapshot {minor} successfully destroyed.")
            return True
        else:
            print(f"Failed to destroy snapshot {minor}. Retrying...")
            retries += 1
            time.sleep(retry_delay)

    print(f"Unable to destroy snapshot {minor} after {max_retries} retries.")
    return False

