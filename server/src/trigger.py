import time
from watchdog.observers import Observer 
from watchdog.events import FileSystemEventHandler 
import subprocess

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Define the command to execute when the file or directory is modified
        command = ['python3', 'backup_snapshot.py']

        # Execute the command
        subprocess.run(command)

if name == "main":
    # Define the directory to monitor
    path = '/backup_pool/backup_data'

    # Create the watchdog observer and event handler
    observer = Observer()
    event_handler = MyHandler()

    # Schedule the event handler to watch the specified directory
    observer.schedule(event_handler, path, recursive=True)

    # Start the observer in a separate thread
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop the observer when Ctrl+C is pressed
        observer.stop()

    # Wait for the observer's thread to terminate
    observer.join()