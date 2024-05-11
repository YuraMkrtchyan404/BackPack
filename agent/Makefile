# This Makefile handles system and Python dependencies, downloads, compiles, and installs external libraries.

# Define default shell used by make, ensuring it can use features like pipefail
SHELL := /bin/bash
APP_DIR=/var/backpack
USER_DIR = /home/$(USER)
DATA_DIR=$(APP_DIR)/data
COW_DIR=$(APP_DIR)/cow
RECOVERY_DIR = $(USER_DIR)/recovery

# Default target executed when no arguments are given to make.
default: full-setup

# Full setup including ownership adjustment, system dependencies, and Python environment.
full-setup: install-prerequisites detect-version download-package install-package install-elastio install-headers compile-install setup-python-env setup-ssh

install-ssh-server:
	@echo "Installing SSH server..."
	@sudo apt-get update
	@sudo apt-get install -y openssh-server
	@echo "SSH server installed successfully."

configure-ssh:
	@echo "Configuring SSH server..."
	@sudo sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config
	@sudo systemctl enable ssh
	@echo "SSH server configured and enabled on boot."

start-ssh:
	@echo "Starting SSH server..."
	@sudo systemctl start ssh
	@echo "SSH server started successfully."

setup-ssh: install-ssh-server configure-ssh start-ssh
	@echo "SSH setup completed successfully."

create-app-dirs:
	@echo "Creating application directories..."
	@sudo mkdir -p $(DATA_DIR) $(COW_DIR) $(RECOVERY_DIR)
	@sudo chown -R $(USER):$(USER) $(APP_DIR)
	@sudo chmod -R 775 $(APP_DIR)

adjust-permissions:
	@echo "Adjusting permissions..."
	@sudo chown -R $(USER):$(USER) $(APP_DIR)
	@sudo chmod -R 775 $(APP_DIR)

configure-sudoers:
	@echo "Configuring sudoers for passwordless file management commands..."
	@echo "$(USER) ALL=(root) NOPASSWD: /bin/mkdir, /bin/rm, /bin/mv, /bin/touch, /bin/chmod, /bin/chown" > /tmp/$(USER)_sudoers
	@sudo cp /tmp/$(USER)_sudoers /etc/sudoers.d/$(USER)_nopasswd
	@sudo chmod 0440 /etc/sudoers.d/$(USER)_nopasswd
	@sudo visudo -c && echo "sudoers file is valid" || echo "Error in sudoers file, not applied"
	@rm /tmp/$(USER)_sudoers

setup-python-env:
	@echo "Setting up Python virtual environment and installing dependencies..."
	@python3 -m venv agentenv
	@. agentenv/bin/activate; pip install -r requirements.txt

install-prerequisites:
	@sudo apt-get update
	@sudo apt-get install -y wget gnupg

detect-version:
	@debian_ver=$$(grep VERSION_ID /etc/os-release | tr -cd [0-9]); \
	if [ $$debian_ver -gt 1000 ]; then \
	    debian_ver=$$(($$debian_ver/200)); \
	fi; \
	echo "Detected Debian/Ubuntu version: $$debian_ver" > debian_version

download-package:
	@source debian_version; \
	wget https://repo.assur.io/master/linux/deb/Debian/$$debian_ver/pool/elastio-repo_0.0.2-1debian$$debian_ver_all.deb

install-package:
	@source debian_version; \
	sudo dpkg -i elastio-repo_0.0.2-1debian$$debian_ver_all.deb
	@sudo apt-get update

install-elastio:
	@sudo apt-get install -y elastio-snap-dkms elastio-snap-utils

install-headers:
	@sudo apt-get install -y linux-headers-$$(uname -r) build-essential

compile-install:
	@cd elastio-snap && \
	sudo make && \
	sudo make install

clean:
	@rm -f *.deb
	@rm -rf agentenv
	@rm -rf debian_version
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name 'pycache' -delete

.PHONY: default full-setup create-app-dirs adjust-permissions setup-python-env install-prerequisites detect-version download-package install-package install-elastio install-headers compile-install clean install-ssh-server configure-ssh start-ssh setup-ssh