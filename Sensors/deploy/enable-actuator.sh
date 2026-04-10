#!/bin/bash

cd /opt/aquadash/sensors/deploy

sudo install -m 0644 actuator.service /etc/systemd/system/actuator.service
sudo systemctl daemon-reload
sudo systemctl enable --now actuator.service
