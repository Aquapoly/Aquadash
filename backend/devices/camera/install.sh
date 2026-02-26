#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

INSTALL_DIR="/opt/aquadash-camera"
BIN_DIR="/usr/local/bin"
SYSTEMD_DIR="/etc/systemd/system"

GROUP_NAME="host-dev"
USER_NAME="camera"

POLICY_NAME="aquadash_camera"
SELINUX_DIR="$SCRIPT_DIR/selinux"

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

# --- Install Python dependencies ---
echo "  Checking system's Python dependencies"
for pkg in imageio opencv-python-headless; do
    if ! python3 -c "import ${pkg//-/_}" 2>/dev/null; then
        echo "  Installing $pkg (required for camera capture)"
        pip3 install "$pkg" --break-system-packages 2>/dev/null || pip3 install "$pkg"
    fi
done

# --- Install camera daemon files ---
echo "  Installing camera daemon to $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
install -m 755 "$SCRIPT_DIR/camera_daemon.py" "$INSTALL_DIR/camera_daemon.py"
install -m 644 "$SCRIPT_DIR/physical_camera.py" "$INSTALL_DIR/physical_camera.py"
install -m 644 "$SCRIPT_DIR/logical_camera.py" "$INSTALL_DIR/logical_camera.py"
install -m 644 "$SCRIPT_DIR/camera_paths.py" "$INSTALL_DIR/camera_paths.py"
install -m 644 "$SCRIPT_DIR/camera_commands.py" "$INSTALL_DIR/camera_commands.py"

# --- Create camera-ctl wrapper in PATH ---
echo "  Installing camera-ctl wrapper to $BIN_DIR"
cat > "$BIN_DIR/camera-ctl" <<EOF
#!/usr/bin/env bash
exec "$INSTALL_DIR/camera-ctl" "\$@"
EOF
install -m 755 "$SCRIPT_DIR/camera-ctl" "$INSTALL_DIR/camera-ctl"
chown root:"$GROUP_NAME" "$BIN_DIR/camera-ctl"
chmod 0750 "$BIN_DIR/camera-ctl"

# --- Install systemd services with path substitution ---
echo "  Installing systemd services"
sed "s|__CAMERA_DIR__|$INSTALL_DIR|g" "$SCRIPT_DIR/camera-daemon.service" \
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
    semanage fcontext -a -t var_run_t '/run/camera' 2>/dev/null || true

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
