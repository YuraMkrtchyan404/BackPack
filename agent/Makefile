SHELL := /bin/bash
APP_DIR=/var/backpack
USER_DIR = /home/$(USER)
DATA_DIR=$(APP_DIR)/data
COW_DIR=$(APP_DIR)/cow
RECOVERY_DIR = $(USER_DIR)/recovery
PYTHON_EXECUTABLE=$(shell which python3)
PYTHON_PATH := $(shell which python3)
SSH_KEY_NAME=backpack_key
SSH_KEY_PATH=$(HOME)/.ssh/$(SSH_KEY_NAME)
SERVER_USER=user1808
SERVER_IP=5.77.254.92
SERVER_PORT=9122

default: full-setup

full-setup: elastio-setup system-setup

elastio-setup: install-prerequisites detect-version download-package install-package install-elastio install-headers compile-install

system-setup: create-app-dirs setup-python-env configure-sudoers generate-ssh-key

create-app-dirs:
	@echo "Creating application directories and adjusting permissions..."
	@sudo mkdir -p $(DATA_DIR) $(COW_DIR) $(RECOVERY_DIR)
	@sudo chown -R $(USER):$(USER) $(APP_DIR)
	@sudo chmod -R 775 $(APP_DIR)

configure-sudoers:
	@echo "Configuring sudoers for passwordless execution of your command..."
	@echo "$(USER) ALL=(ALL) NOPASSWD: /bin/mkdir, /bin/rm, /bin/mv, /bin/touch, /bin/chmod, /bin/chown, /usr/bin/elioctl, $(PYTHON_PATH) -m src.cron_snapshot" | sudo EDITOR='tee -a' visudo

setup-python-env:
	@echo "Setting up Python virtual environment and installing dependencies..."
	@$(PYTHON_EXECUTABLE) -m venv agentenv && \
	source agentenv/bin/activate && \
	pip install -r requirements.txt

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

generate-ssh-key:
	@echo "Generating SSH keys for secure communication..."
	@if [ ! -f $(SSH_KEY_PATH) ]; then \
		ssh-keygen -t rsa -b 4096 -f $(SSH_KEY_PATH) -N ""; \
		echo "SSH key generated at $(SSH_KEY_PATH)"; \
	else \
		echo "SSH key already exists at $(SSH_KEY_PATH)"; \
	fi
	@echo "Copying public key to the server..."
	@ssh-copy-id -i $(SSH_KEY_PATH).pub -p $(SERVER_PORT) $(SERVER_USER)@$(SERVER_IP)
	@chmod 600 $(SSH_KEY_PATH)


clean:
	@rm -f *.deb
	@rm -rf agentenv
	@rm -rf backpack.egg-info
	@rm -rf debian_version main.spec
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -delete

.PHONY: default full-setup create-app-dirs setup-python-env install-prerequisites detect-version download-package install-package install-elastio install-headers compile-install clean configure-sudoers generate-ssh-key elastio-setup system-setup