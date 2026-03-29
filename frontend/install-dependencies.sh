#!/bin/bash

set -euo pipefail

# Frontend-focused dependency installer.
# Purpose: ensure Node/NPM are available and install frontend Node modules.
# This script intentionally does NOT modify system packages or install Docker.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is not installed. Please install Node.js (LTS) using nvm or your OS package manager." >&2
  echo "Recommended: https://github.com/nvm-sh/nvm or https://nodejs.org/" >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found. Ensure Node.js installation includes npm." >&2
  exit 1
fi

echo "Installing frontend dependencies (in $(pwd))..."
if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi

echo "Frontend dependencies installed. Use 'npm start' to run dev server or 'npm run build' to build." 
