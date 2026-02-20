from pathlib import Path

# normally created by systemd
SOCK_DIR: Path = Path("/run/camera")

# per-device symlinks
CURRENT_DIR: Path = SOCK_DIR / "current"

# control endpoint for daemon
CONTROL_SOCKET: Path = SOCK_DIR / "control.sock"