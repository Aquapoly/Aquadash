#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="/opt/aquadash-camera"
BIN_DIR="/usr/local/bin"
SYSTEMD_DIR="/etc/systemd/system"

GROUP_NAME="host-dev"
USER_NAME="camera"

SERVICES=("camera-daemon.service")

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
echo "  Removing camera-ctl wrapper from $BIN_DIR"
rm -f "$BIN_DIR/camera-ctl"

echo "  Removing camera daemon from $INSTALL_DIR"
rm -rf "$INSTALL_DIR"

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

# --- Remove SELinux policy (if installed) ---
if command -v selinuxenabled >/dev/null 2>&1 && selinuxenabled; then
    echo "  Removing SELinux camera policy..."

    semodule -r aquadash_camera >/dev/null 2>&1 || true
    semanage fcontext -d '/run/camera(/.*)?' >/dev/null 2>&1 || true
    restorecon -Rv /run/camera >/dev/null 2>&1 || true
fi

echo ""
echo "==> Done. Aquadash camera service fully removed."
