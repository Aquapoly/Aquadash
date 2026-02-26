# Camera Service

A systemd-managed daemon that exposes camera devices via Unix sockets for containerized applications.

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│ Host System                                                │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ camera-daemon.service (systemd)                      │  │
│  │ - Runs as root:host-dev                              │  │
│  │ - Manages /run/camera/ directory                     │  │
│  │ - Creates RuntimeDirectory with 0750 permissions     │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                │
│                           ▼                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ /run/camera/                                         │  │
│  │ ├── control.sock (0660 root:host-dev)                │  │
│  │ ├── video0.sock  (0660 root:host-dev) [per camera]   │  │
│  │ └── top-cam.sock  (0660 root:host-dev) [per camera]  │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                │
│                           │ (read-only mount)              │
└───────────────────────────┼────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│ Docker Container (backend)                                 │
│ - Runs with --group-add host-dev                           │
│ - Mounts /run/camera:/run/camera:ro                        │
│ - Reads frames from camera sockets                         │
└────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.x with pip
- systemd
- Root access (sudo)

### Install

```bash
cd backend/deployment/devices/camera
sudo ./install.sh
```

This will:

1. Create `host-dev` group and `camera` system user
2. Install Python dependencies (imageio)
3. Copy daemon files to `/opt/aquadash-camera/`
4. Create wrapper script at `/usr/local/bin/camera-ctl`
5. Install systemd service files

### Uninstall

```bash
sudo ./uninstall.sh
```

This will:

1. Stop and remove systemd services
2. Remove installed files from `/opt/aquadash-camera/` and `/usr/local/bin/`
3. Remove `camera` user and `host-dev` group (if empty)

## Usage

### Daemon Lifecycle (systemctl)

```bash
# Start daemon
sudo systemctl start camera-daemon.service

# Stop daemon
sudo systemctl stop camera-daemon.service

# Enable auto-start on boot
sudo systemctl enable camera-daemon.service

# Check status
sudo systemctl status camera-daemon.service

# View logs
sudo journalctl -u camera-daemon.service -f
```

### Camera Management (camera-ctl)

```bash
# Create a (logical) camera on specified device (its name will be the literal device name)
sudo camera-ctl create /dev/video0  # Created camera named video0

# Create a (logical) camera with specified name on specified device
sudo camera-ctl create front-cam /dev/video1

# List active cameras
sudo camera-ctl list

# Remove a camera by its logical name (e.g. default camera on /dev/video0)
sudo camera-ctl remove video0

# Show help
sudo camera-ctl --help
```

Mounting a camera on a device that does not currently exist or may not continue to exist indefinitely is perfectly allowed. This means that you can hot-plug your a camera at some device location.

You may also use the rewire capabilities to swap a logical camera's data stream from a device to another without shutting anything down.

**Note:** `camera-ctl` requires sudo or membership in the `host-dev` group.

## Protocol

### Control Socket

- **Path:** `/run/camera/control.sock`
- **Commands:**
  - `ADD_CAMERA <device_path>` — Expose a camera device
  - `REMOVE_CAMERA <device_path>` — Remove a camera device
  - `LIST_CAMERAS` — List active camera devices

### Camera Sockets

- **Path:** `/run/camera/<device_name>.sock` (e.g., `video0.sock` for `/dev/video0`)
- **Protocol:** Length-prefixed PNG frames
  1. Client connects to socket
  2. Server sends 4-byte big-endian frame length
  3. Server sends PNG frame bytes
  4. Connection closes

Example Python client:

```python
import socket

def read_frame(sock_path):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(sock_path)
        size = int.from_bytes(s.recv(4), "big")
        frame = b""
        while len(frame) < size:
            chunk = s.recv(size - len(frame))
            if not chunk:
                raise ConnectionError("Socket closed")
            frame += chunk
        return frame

frame_png = read_frame("/run/camera/video0.sock")
```

## Security

### Permissions

- `/run/camera/` directory: `0750 root:host-dev`
- Control socket: `0660 root:host-dev`
- Camera sockets: `0660 root:host-dev`
- `camera-ctl` wrapper: `0750 root:host-dev`

### Access Control

Only users in the `host-dev` group can:

- Execute `camera-ctl`
- Connect to control socket
- Read from camera sockets

To grant access to a user:

```bash
sudo usermod -aG host-dev <username>
```

### SELinux

If SELinux is enforcing and you encounter permission errors, ensure Python has the correct context:

```bash
sudo restorecon -v /usr/bin/python3*
```

## Files

### Installed Files

- `/opt/aquadash-camera/camera_daemon.py` — Main daemon executable
- `/opt/aquadash-camera/camera.py` — Camera class
- `/opt/aquadash-camera/camera_paths.py` — Path constants
- `/opt/aquadash-camera/camera_commands.py` — Command enum
- `/opt/aquadash-camera/camera-ctl` — CLI tool
- `/usr/local/bin/camera-ctl` — Wrapper script (restricted to host-dev)
- `/etc/systemd/system/camera-daemon.service` — Systemd service unit

### Source Files

- `camera_daemon.py` — Daemon implementation
- `camera.py` — Per-camera socket server
- `camera_paths.py` — Shared path constants
- `camera_commands.py` — Command protocol definitions
- `camera-ctl` — CLI tool
- `camera-daemon.service` — Service template (uses `__CAMERA_DIR__` placeholder)
- `install.sh` — Installation script
- `uninstall.sh` — Uninstallation script

## Troubleshooting

### Daemon won't start (exit code 203)

**Symptom:** `systemctl status` shows `Main PID: ... (code=exited, status=203/EXEC)`

**Causes:**

1. SELinux blocking Python execution
2. Missing execute permissions on daemon file

**Solutions:**

```bash
# Fix SELinux context
sudo restorecon -v /usr/bin/python3*

# Verify daemon is executable
ls -l /opt/aquadash-camera/camera_daemon.py
# Should show: -rwxr-xr-x
```

### Daemon crashes (exit code 1)

**Check logs:**

```bash
sudo journalctl -u camera-daemon.service -n 50
```

**Common issues:**

- Missing `imageio` dependency (should be auto-installed by `install.sh`)
- Permission denied accessing `/dev/video*` (daemon runs as root, should have access)
- Socket binding errors (check if `/run/camera/` exists and has correct permissions)

### camera-ctl: Permission denied

**Symptom:** `bash: /usr/local/bin/camera-ctl: Permission denied`

**Solution:** Run as root (`sudo`), or add your user to the `host-dev` group:

```bash
sudo usermod -aG host-dev $USER
# Log out and back in for group membership to take effect
```

### No cameras detected

**Check available devices:**

```bash
ls -l /dev/video*
```

**Add camera manually:**

```bash
sudo camera-ctl add /dev/video0
```

### Backend can't connect to camera socket

**Verify:**

1. Daemon is running: `sudo systemctl status camera-daemon.service`
2. Camera is added: `sudo camera-ctl list`
3. Socket exists: `sudo ls -l /run/camera/`
4. Backend container has `--group-add host-dev` and mounts `/run/camera:/run/camera:ro`

## Development

### Testing Changes

After modifying source files, reinstall:

```bash
sudo ./uninstall.sh
sudo ./install.sh
sudo systemctl start camera-daemon.service
```

### Running Manually (for debugging)

```bash
# Stop systemd service first
sudo systemctl stop camera-daemon.service

# Run daemon in foreground
sudo python3 /opt/aquadash-camera/camera_daemon.py
```

## Integration with Backend

The backend's `app/services/camera.py` connects to camera sockets in `/run/camera/`:

```python
# backend/app/services/camera.py
CAMERA_SOCK_DIR = Path("/run/camera")

def _fetch_frame() -> bytes:
    sockets = [s for s in CAMERA_SOCK_DIR.glob("*.sock")
               if s.name != "control.sock"]
    if not sockets:
        raise OSError("No camera available")

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(str(sockets[0]))
        size = int.from_bytes(s.recv(4), "big")
        return s.recv(size)
```

The backend container must:

1. Mount `/run/camera:/run/camera:ro`
2. Run with `--group-add $(getent group host-dev | cut -d: -f3)`
3. Ensure user inside container is in the host-dev group

See `backend/deployment/backend-container.service` for the complete configuration.
