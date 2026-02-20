#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_DIR="$(dirname "$SCRIPT_DIR")"

BIN_DIR="/usr/local/bin"
SYSTEMD_DIR="/etc/systemd/system"

GROUP_NAME="host-dev"
USER_NAME="camera"

echo "==> Installing Aquadash camera service"

# --- System group and user ---
if ! getent group "$GROUP_NAME" > /dev/null 2>&1; then
    echo "  Creating group: $GROUP_NAME"
    groupadd --system "$GROUP_NAME"
else
    echo "  Group already exists: $GROUP_NAME"
fi

if ! id "$USER_NAME" > /dev/null 2>&1; then
    echo "  Creating user: $USER_NAME"
    useradd --system --home /nonexistent --shell /usr/sbin/nologin "$USER_NAME"
else
    echo "  User already exists: $USER_NAME"
fi

if ! id -nG "$USER_NAME" | grep -qw "$GROUP_NAME"; then
    echo "  Adding $USER_NAME to $GROUP_NAME"
    usermod -aG "$GROUP_NAME" "$USER_NAME"
fi

# --- Python daemon scripts ---
echo "  Copying daemon scripts to $BIN_DIR"
install -m 755 "$SCRIPT_DIR/camera_daemon.py" "$BIN_DIR/camera-daemon.py"
install -m 644 "$SCRIPT_DIR/camera.py"        "$BIN_DIR/camera.py"
install -m 644 "$SCRIPT_DIR/camera_paths.py"  "$BIN_DIR/camera_paths.py"

# --- camera-ctl helper ---
echo "  Installing camera-ctl to $BIN_DIR"
install -m 755 "$SCRIPT_DIR/camera-ctl" "$BIN_DIR/camera-ctl"

# --- Systemd services ---
echo "  Installing systemd services"
install -m 644 "$SCRIPT_DIR/camera-daemon.service"         "$SYSTEMD_DIR/camera-daemon.service"
install -m 644 "$DEPLOYMENT_DIR/backend-container.service" "$SYSTEMD_DIR/backend-container.service"

systemctl daemon-reload

echo ""
echo "==> Installation complete."
echo ""
echo "To start the camera service now:"
echo "  sudo systemctl start camera-daemon.service"
echo "  sudo systemctl start backend-container.service"
echo ""
echo "To start automatically on boot:"
echo "  sudo systemctl enable camera-daemon.service"
echo "  sudo systemctl enable backend-container.service"
echo ""
echo "To add a camera once the daemon is running:"
echo "  camera-ctl add /dev/video0"
