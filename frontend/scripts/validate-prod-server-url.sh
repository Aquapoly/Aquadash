#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../src/app/environment.ts"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[Error] $ENV_FILE not found. Create it from environment.example.ts." >&2
  exit 1
fi

server_url_line="$(grep -E "^export const SERVER_URL\s*=\s*'" "$ENV_FILE" || true)"
if [[ -z "$server_url_line" ]]; then
  server_url_line="$(grep -E '^export const SERVER_URL\s*=\s*"' "$ENV_FILE" || true)"
fi

if [[ -z "$server_url_line" ]]; then
  echo "[Error] Could not find SERVER_URL export in $ENV_FILE" >&2
  exit 1
fi

server_url="$(
  printf '%s' "$server_url_line" |
    sed -E "s/^export const SERVER_URL\s*=\s*['\"]([^'\"]+)['\"];?\s*$/\1/"
)"

host="$(printf '%s' "$server_url" | sed -E 's#^[a-zA-Z][a-zA-Z0-9+.-]*://##' | cut -d'/' -f1 | sed -E 's/:.*$//')"

# Disallow actual loopback/localhost hosts
case "$host" in
  localhost|127.0.0.1|0.0.0.0|::1)
    echo "[Error] Refusing to deploy: SERVER_URL host is '$host' in $ENV_FILE" >&2
    echo "[Error] Set SERVER_URL to your backend's reachable hostname/IP (not localhost)." >&2
    exit 1
    ;;
esac
