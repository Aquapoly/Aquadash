#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "$SCRIPT_DIR/../src/app" && pwd)"

ensure_file_from_example() {
  local target="$1"
  local example="$2"

  if [[ -f "$target" ]]; then
    return 0
  fi

  if [[ ! -f "$example" ]]; then
    echo "[Error] Missing example file: $example" >&2
    exit 1
  fi

  cp "$example" "$target"
  echo "[Info] Created $target from $example"
}

ensure_file_from_example "$APP_DIR/environment.ts" "$APP_DIR/environment.example.ts"
ensure_file_from_example "$APP_DIR/app-settings.ts" "$APP_DIR/app-settings.example.ts"
