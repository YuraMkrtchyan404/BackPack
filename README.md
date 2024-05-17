# Backpack - A Snapshot-Based Backup and Recovery System

## Introduction

Backpack is a CLI application designed to provide a robust backup and recovery solution for Ubuntu systems (versions earlier than 22.04). It utilizes block-level snapshots created with the `elastio-snap` open source kernel module. After extracting the selected folder from the mounted block-level snapshot, the data is transferred to the server using `rsync` over SSH. The project leverages ZFS (Zettabyte File System) for snapshot management on the server side, allowing users to capture the state of entire directories at precise moments in time. Once the data reaches the server successfully, a ZFS snapshot is taken to maintain the backup history. These snapshots can then be transferred over a network for backup or recovery purposes using `rsync` and SSH, with gRPC facilitating remote procedure calls between the client and server. Additionally, backups can be scheduled using cronjobs, which provide different options for backup frequency.

## Usage

### Commands

#### `start` Command

This command initiates the backup process. It has two modes: manual and auto.

- **Manual Mode:**  
  Prompts users to enter the folder(s) to perform the backup.

  ```sh
  backpack start manual
- **Auto Mode:**

  ```sh
  backpack start auto

#### `list` Command

The list command lists all available snapshots. If a folder name is specified, it lists snapshots only for that particular folder.
- **Without folder_name:**  
  Lists all snapshots on the server.

  ```sh
  backpack list
- **With folder_name:**
  Lists snapshots for a specified folder.
  ```sh
  backpack list your_folder_name

#### `recover` Command

This command recovers a specific snapshot with the chosen mode.
- **Original Mode:**  
  Recovers the snapshot to its original state.

  ```sh
  backpack recover your_snapshot_name original
- **Standard Mode:**
  Recovers the snapshot to a predefined path /home/{user_name}/recovered.
  ```sh
  backpack recover your_snapshot_name standard

