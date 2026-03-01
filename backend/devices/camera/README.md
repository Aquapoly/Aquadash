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
│ Docker Container (cam_client)                              │
│ - Runs with group host-dev                                 │
│ - Mounts /run/camera:/run/camera:z                         │
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
2. Copy daemon files to `/opt/aquadash-camera/`
3. Create wrapper script at `/usr/local/bin/camera-ctl`
4. Install systemd service files

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
# Create a camera on specified device (its logical name will be the literal device name)
sudo camera-ctl create /dev/video0  # Created camera named video0

# Create a camera with specified logical name on specified device
sudo camera-ctl create front-cam /dev/video1

# Remove a camera by its logical name (e.g. default camera on /dev/video0)
sudo camera-ctl remove video0

# List active cameras
sudo camera-ctl list

# Get group id of host-dev
sudo camera-ctl gid

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
  - `create <logical_name> <device_path>` — Expose a camera device
  - `remove <logical_name>` — Remove a camera device
  - `list` — List active camera devices

### Camera Sockets

- **Path:** `/run/camera/<device_name>.sock` (e.g., `video0.sock` for `/dev/video0`)
- **Protocol:** Length-prefixed PNG frames
  1. Client connects to socket
  2. Server sends 4-byte big-endian frame length
  3. Server sends PNG frame bytes
  4. Connection closes

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

## Files

### Installed Files

- `/opt/aquadash-camera/camera_daemon.py` — Main daemon executable
- `/opt/aquadash-camera/logical_camera.py` — LogicalCamera class
- `/opt/aquadash-camera/physical_camera.py` — PhysicalCamera class
- `/opt/aquadash-camera/camera_paths.py` — Path constants
- `/opt/aquadash-camera/camera_commands.py` — Command enum
- `/opt/aquadash-camera/camera-ctl` — CLI tool
- `/usr/local/bin/camera-ctl` — Wrapper script (restricted to host-dev)
- `/etc/systemd/system/camera-daemon.service` — Systemd service unit

### Source Files

- `camera_daemon.py` — Daemon implementation
- `logical_camera.py` — Per-camera socket server
- `physical_camera.py` — Manages access to hardware by logical cameras
- `camera_paths.py` — Shared path constants
- `camera_commands.py` — Command protocol definitions
- `camera-ctl` — CLI tool
- `camera-daemon.service` — Service template (uses `__CAMERA_DIR__` placeholder)
- `install.sh` — Installation script
- `uninstall.sh` — Uninstallation script
- `requirements.txt` — Requirements used by the installation script

## Troubleshooting

### Daemon crashes (exit code 1)

**Check logs:**

```bash
sudo journalctl -u camera-daemon.service -n 50
```

**Common issues:**

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
4. cam-client container has group `host-dev` and mounts `/run/camera:/run/camera:z`

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
sudo /opt/aquadash-camera/.venv/bin/python /opt/aquadash-camera/camera_daemon.py
```

## Integration With Backend

The cam-client container connects to camera sockets in `/run/camera/`:

The cam-client container must:

1. Mount `/run/camera:/run/camera:z`
2. Run with group host-dev, e.g. `--group-add $(getent group host-dev | cut -d: -f3)`
