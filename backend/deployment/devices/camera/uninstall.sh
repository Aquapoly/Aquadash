#!/usr/bin/env bash
set -euo pipefail

BIN_DIR="/usr/local/bin"
SYSTEMD_DIR="/etc/systemd/system"

GROUP_NAME="host-dev"
USER_NAME="camera"

SERVICES=("camera-daemon.service" "backend-container.service")

echo "==> Uninstalling Aquadash camera service"

# --- Stop, disable, and remove systemd services ---
for svc in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "$svc" 2>/dev/null; then
        echo "  Stopping $svc"
        systemctl stop "$svc"
    fi
    if systemctl is-enabled --quiet "$svc" 2>/dev/null; then
        echo "  Disabling $svc"
        systemctl disable "$svc"
    fi
    if [ -f "$SYSTEMD_DIR/$svc" ]; then
        echo "  Removing $SYSTEMD_DIR/$svc"
        rm -f "$SYSTEMD_DIR/$svc"
    fi
done

systemctl daemon-reload

# --- Remove installed files ---
echo "  Removing files from $BIN_DIR"
rm -f "$BIN_DIR/camera-daemon.py"
rm -f "$BIN_DIR/camera.py"
rm -f "$BIN_DIR/camera_paths.py"
rm -f "$BIN_DIR/camera-ctl"

# --- Remove user ---
if id "$USER_NAME" > /dev/null 2>&1; then
    echo "  Removing user: $USER_NAME"
    userdel "$USER_NAME"
fi

# --- Remove group (only if no remaining members) ---
if getent group "$GROUP_NAME" > /dev/null 2>&1; then
    members="$(getent group "$GROUP_NAME" | cut -d: -f4)"
    if [ -z "$members" ]; then
        echo "  Removing group: $GROUP_NAME"
        groupdel "$GROUP_NAME"
    else
        echo "  Skipping group removal: $GROUP_NAME still has members ($members)"
    fi
fi

echo ""
echo "==> Done. Aquadash camera service fully removed."
