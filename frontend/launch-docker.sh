#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

bash ./scripts/ensure-local-config.sh
bash ./scripts/validate-prod-server-url.sh

npm ci
npm run build
docker build -t aquadash .
docker run --rm -d -p 80:80 --name aquadash aquadash