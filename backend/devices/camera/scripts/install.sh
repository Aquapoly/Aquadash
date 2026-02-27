#!/usr/bin/env bash
set -euo pipefail

HOST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../host"

INSTALL_DIR="/opt/aquadash-camera"
BIN_DIR="/usr/local/bin"
SYSTEMD_DIR="/etc/systemd/system"

GROUP_NAME="host-dev"
USER_NAME="camera"

POLICY_NAME="aquadash_camera"
SELINUX_DIR="$HOST_DIR/selinux"

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

# --- Install camera daemon files ---
echo "  Installing camera daemon to $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
chown -R root:"$GROUP_NAME" "$INSTALL_DIR"
chmod -R 750 "$INSTALL_DIR"

install -m 644 "$HOST_DIR"/*.py "$INSTALL_DIR"
install -m 755 "$HOST_DIR/camera_daemon.py" "$INSTALL_DIR"

# --- Create virtual environment ---
echo "  Creating Python virtual environment..."
python3 -m venv "$INSTALL_DIR/.venv"

echo "  Installing Python dependencies into venv..."
"$INSTALL_DIR/.venv/bin/pip" install --upgrade pip --quiet
"$INSTALL_DIR/.venv/bin/pip" install -r "$HOST_DIR/requirements.txt" --quiet

# --- Create camera-ctl wrapper in PATH ---
echo "  Installing camera-ctl wrapper to $BIN_DIR"
cat > "$BIN_DIR/camera-ctl" <<EOF
#!/usr/bin/env bash
exec "$INSTALL_DIR/camera-ctl" "\$@"
EOF
install -m 755 "$HOST_DIR/camera-ctl" "$INSTALL_DIR/camera-ctl"
chown root:"$GROUP_NAME" "$BIN_DIR/camera-ctl"
chmod 0750 "$BIN_DIR/camera-ctl"

# --- Install systemd services with path substitution ---
echo "  Installing systemd services"
sed "s|__CAMERA_DIR__|$INSTALL_DIR|g" "$HOST_DIR/camera-daemon.service" \
    > "$SYSTEMD_DIR/camera-daemon.service"
systemctl daemon-reload

# --- SELinux setup (if enabled) ---
if command -v selinuxenabled >/dev/null 2>&1 && selinuxenabled; then
    echo "  Configuring SELinux policy..."

    # Compile and install module
    checkmodule -M -m -o "$SELINUX_DIR/$POLICY_NAME.mod" "$SELINUX_DIR/$POLICY_NAME.te"
    semodule_package -o "$SELINUX_DIR/$POLICY_NAME.pp" -m "$SELINUX_DIR/$POLICY_NAME.mod"
    semodule -i "$SELINUX_DIR/$POLICY_NAME.pp"

    # Apply file context
    semanage fcontext -a -t camera_socket_t '/run/camera/[^/]+\.sock' 2>/dev/null || true
    if ! semanage fcontext -l | grep -q '/run/camera'; then
        semanage fcontext -a -t var_run_t '/run/camera'
    else
        semanage fcontext -m -t var_run_t '/run/camera'
    fi

    echo "  SELinux policy installed"
fi

echo ""
echo "==> Installation complete."
echo ""
echo "Daemon lifecycle (use systemctl):"
echo "  sudo systemctl start camera-daemon.service    # Start daemon"
echo "  sudo systemctl stop camera-daemon.service     # Stop daemon"
echo "  sudo systemctl enable camera-daemon.service   # Auto-start on boot"
echo "  sudo systemctl status camera-daemon.service   # Check status"
echo ""
echo "Camera management (use camera-ctl):"
echo "  sudo camera-ctl --help                        # Show usage"
