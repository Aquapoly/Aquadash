#!/bin/bash

# Get the current user
CURRENT_USER=$(whoami)

# Set the full path for actuator.py
SCRIPT_DIR=$(pwd)
SCRIPT_PATH="$SCRIPT_DIR/services/actuator.py"
SERVICE_FILE="/etc/systemd/system/actuator.service"

# Make actuator.py executable
chmod +x "$SCRIPT_PATH"

# Create the systemd service file with the current user as the User
echo "[Unit]
Description=Actuator Check Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 $SCRIPT_PATH
Restart=always
User=$CURRENT_USER
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target" | sudo tee $SERVICE_FILE > /dev/null

# Reload systemd, start, and enable the service
sudo systemctl daemon-reload
sudo systemctl start actuator.service
sudo systemctl enable actuator.service

echo "Service actuator has been set up, started, and will run on startup."