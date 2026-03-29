#!/bin/bash
set -euo pipefail
npm ci
npm run build
docker build -t aquadash .
docker run --rm -d -p 80:80 --name aquadash aquadash