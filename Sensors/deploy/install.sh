#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SENSORS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

sudo mkdir -p /opt/aquadash
sudo ln -sfn "$SENSORS_DIR" /opt/aquadash/sensors
