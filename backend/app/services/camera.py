import socket
import time
from pathlib import Path

CAMERA_CURRENT_DIR = Path("/run/camera/current")
IMAGE_EXPIRE_TIME = 5

_last_image: tuple[bytes, float] | None = None


def _read_exact(sock: socket.socket, n: int) -> bytes:
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Camera daemon closed connection unexpectedly")
        data += chunk
    return data


def _fetch_frame() -> bytes:
    """Connect to the first available camera socket and retrieve one PNG frame."""
    sockets = list(CAMERA_CURRENT_DIR.iterdir()) if CAMERA_CURRENT_DIR.exists() else []
    if not sockets:
        raise OSError("No camera available")

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(str(sockets[0]))
        size = int.from_bytes(_read_exact(s, 4), "big")
        return _read_exact(s, size)


def get_image() -> bytes:
    """
    Retrieves the latest camera image, refreshing it if expired.
    Returns:
        bytes: The PNG-encoded image bytes.
    Raises:
        OSError: If no camera is available and there is no cached image.
    """
    global _last_image

    if _last_image is not None and _last_image[1] >= time.time():
        return _last_image[0]

    im = None
    try:
        im = _fetch_frame()
    except Exception:
        pass

    if im is not None:
        _last_image = (im, time.time() + IMAGE_EXPIRE_TIME)

    if _last_image is None:
        raise OSError("Camera not available")

    return _last_image[0]
