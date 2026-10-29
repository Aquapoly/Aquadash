#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$SCRIPT_DIR/disable-crontab-jobs.sh" || true
"$SCRIPT_DIR/disable-actuator.sh" || true

if [[ -f /etc/systemd/system/actuator.service ]]
then
  sudo rm -f /etc/systemd/system/actuator.service
  sudo systemctl daemon-reload
fi

if [[ -L /opt/aquadash/sensors ]]
then
  sudo rm -f /opt/aquadash/sensors
fi