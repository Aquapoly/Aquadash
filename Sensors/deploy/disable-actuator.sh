#!/bin/bash

# Stop and disable the actuator service
sudo systemctl stop actuator.service
sudo systemctl disable actuator.service
