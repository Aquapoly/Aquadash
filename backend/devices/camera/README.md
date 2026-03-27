Here's the rewritten README:

# Camera Service

A systemd-managed daemon that exposes host camera devices via Unix sockets to containerized applications.

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
│  │ ├── webcam.sock  (0660 root:host-dev) [per camera]   │  │
│  │ └── top-cam.sock (0660 root:host-dev) [per camera]   │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                │
│                           │ (bind mount)                   │
└───────────────────────────┼────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│ Docker Container (cam-client)                              │
│ - Runs as 1000:host-dev                                    │
│ - Mounts /run/camera:/run/camera:z                         │
│ - Reads frames from camera sockets                         │
└────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.x with pip
- systemd
- Root access (sudo)
- SELinux (optional — policy module installed automatically if enabled)

### Install

```bash
sudo ./backend/devices/camera/scripts/install.sh
```

This will:

1. Create the `host-dev` group and `camera` system user
2. Copy daemon files to `/opt/aquadash-camera/` and set up a Python virtual environment
3. Install a `camera-ctl` wrapper at `/usr/local/bin/camera-ctl`
4. Install and register the `camera-daemon` systemd service
5. Install the SELinux policy module if SELinux is enabled

### Uninstall

```bash
sudo ./backend/devices/camera/scripts/uninstall.sh
```

This will:

1. Stop and disable the systemd service and remove its unit file
2. Remove installed files from `/opt/aquadash-camera/` and `/usr/local/bin/`
3. Remove the `camera` user and `host-dev` group (if no remaining members)
4. Remove the SELinux policy module if SELinux is enabled

## Usage

### Daemon Lifecycle

```bash
sudo systemctl start camera-daemon.service    # Start
sudo systemctl stop camera-daemon.service     # Stop
sudo systemctl enable camera-daemon.service   # Enable auto-start on boot
sudo systemctl status camera-daemon.service   # Check status
sudo journalctl -u camera-daemon.service -f   # Follow logs
```

### Camera Management

```bash
# Create a logical camera with an explicit name on a device
sudo camera-ctl create front-cam /dev/video0

# Create a logical camera using the device name as the logical name
sudo camera-ctl create /dev/video0            # Results in logical name "video0"

# Rewire a logical camera to a different physical device
sudo camera-ctl rewire front-cam /dev/video1

# Remove a logical camera
sudo camera-ctl remove front-cam

# List active logical cameras
sudo camera-ctl list

# Get the GID of the host-dev group
sudo camera-ctl gid

# Show help
sudo camera-ctl --help
```

Mounting a logical camera on a device that does not currently exist is allowed — the daemon will serve frames as soon as the device becomes available. This enables hot-plugging: you can register a camera before physically connecting it. Likewise, you can disconnect it at will after that.

**Note:** `camera-ctl` requires `sudo` or membership in the `host-dev` group.

## Protocol

### Control Socket

- **Path:** `/run/camera/control.sock`
- **Commands:** `create`, `rewire`, `remove`, `list`, `gid` (see `camera-ctl --help`)

### Camera Sockets

- **Path:** `/run/camera/<logical_name>.sock`
- **Protocol:** Length-prefixed PNG frames
  1. Client connects to socket
  2. Server sends 4-byte big-endian frame length
  3. Server sends PNG frame bytes
  4. Connection closes

## Security

### Permissions

| Path                        | Mode   | Owner           |
| --------------------------- | ------ | --------------- |
| `/run/camera/`              | `0750` | `root:host-dev` |
| `/run/camera/control.sock`  | `0660` | `root:host-dev` |
| `/run/camera/<name>.sock`   | `0660` | `root:host-dev` |
| `/usr/local/bin/camera-ctl` | `0750` | `root:host-dev` |

Only members of `host-dev` can execute `camera-ctl` and connect to camera sockets. To grant access to a user:

```bash
sudo usermod -aG host-dev <username>
# Log out and back in for group membership to take effect
```

### SELinux

If SELinux is enabled, the install script automatically compiles and loads a policy module (`camera_container`) that permits `cam-client` to connect to camera sockets across the container boundary. The uninstall script removes it.

## Source Files

| File                          | Description                                           |
| ----------------------------- | ----------------------------------------------------- |
| `camera_daemon.py`            | Main daemon entry point                               |
| `logical_camera.py`           | Per-camera Unix socket server                         |
| `physical_camera.py`          | Physical device access, shared across logical cameras |
| `camera_paths.py`             | Shared path constants                                 |
| `camera_commands.py`          | Control protocol command definitions                  |
| `camera-ctl`                  | CLI tool                                              |
| `camera-daemon.service`       | Systemd service unit template                         |
| `scripts/install.sh`          | Installation script                                   |
| `scripts/uninstall.sh`        | Uninstallation script                                 |
| `requirements.txt`            | Python dependencies                                   |
| `selinux/camera_container.te` | SELinux policy source                                 |

## Troubleshooting

### Daemon fails to start

```bash
sudo journalctl -u camera-daemon.service -n 50
```

Common causes:

- `/run/camera/` permissions incorrect — the service recreates this directory on start, so a manual `rm -rf /run/camera` followed by a restart could resolve it
- SELinux denying execution — check `sudo ausearch -m avc -ts recent` and ensure the policy module is loaded (`sudo semodule -l | grep camera`)

### `camera-ctl: Permission denied`

Run with `sudo`, or add your user to `host-dev` and re-login:

```bash
sudo usermod -aG host-dev $USER
```

### `cam-client` cannot connect to camera socket

Verify in order:

1. Daemon is running: `sudo systemctl status camera-daemon.service`
2. Camera is registered: `sudo camera-ctl list`
3. Socket exists: `sudo ls -la /run/camera/`
4. `cam-client` mounts `/run/camera` and runs with the `host-dev` GID

### Running the daemon manually (for debugging)

```bash
sudo systemctl stop camera-daemon.service
sudo /opt/aquadash-camera/.venv/bin/python /opt/aquadash-camera/camera_daemon.py
```

### Reinstalling after source changes

```bash
sudo ./backend/devices/camera/scripts/uninstall.sh
sudo ./backend/devices/camera/scripts/install.sh
sudo systemctl start camera-daemon.service
```
