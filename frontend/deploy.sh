#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

bash ./scripts/ensure-local-config.sh
bash ./scripts/validate-prod-server-url.sh

npm run build && \
sudo rm -rf /var/www/aquadash && \
sudo mkdir -p /var/www/aquadash && \
sudo cp -r dist/aquadash/* /var/www/aquadash/
