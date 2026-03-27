import os
from socket import socket, AF_UNIX, SOCK_STREAM
import time
from pathlib import Path

class CameraSocketNotFoundError(BrokenPipeError):
    pass

class CameraNotAvailableError(ConnectionError):
    pass

class CameraClient:
    CAMERA_SOCK_DIR = Path("/run/camera")

    IMAGE_EXPIRE_TIME = 5

    def __init__(self, camera_name: str):
        self.sock_path: Path = Path(self.CAMERA_SOCK_DIR / f"{camera_name}.sock")
        self.last_image: tuple[bytes, float] | None = None
    
    def _ensure_socket(self):
        if self.sock_path is None or not self.sock_path.exists():
            raise CameraSocketNotFoundError(self.sock_path)

    @staticmethod
    def _read_exact(sock: socket, n: int) -> bytes:
        data = b""
        while len(data) < n:
            chunk = sock.recv(n - len(data))
            if not chunk:
                raise CameraNotAvailableError()
            data += chunk
        return data
    
    def _fetch_frame(self) -> bytes:
        """Connect to camera socket and retrieve one frame."""
        self._ensure_socket()
        with socket(AF_UNIX, SOCK_STREAM) as s:
            s.connect(str(self.sock_path))
            size = int.from_bytes(CameraClient._read_exact(s, 4), "big")
            return CameraClient._read_exact(s, size)

    def capture(self) -> bytes:
        """Always fetches a fresh frame directly from the camera socket."""
        return self._fetch_frame()

    def get_image(self) -> bytes:
        """
        Retrieves the latest camera image, refreshing it if expired.
        Returns:
            bytes: The PNG-encoded image bytes.
        Raises:
            PermissionError: If the container is ill-defined for socket access.
            CameraSocketNotFoundError: If no camera socket is mounted.
            CameraNotAvailableError: If no camera is available and there is no cached image.
        """
        call_time: float = time.time()

        # Use cache if it's too soon
        if self.last_image is not None and self.last_image[1] >= call_time:
            return self.last_image[0]

        im = self.capture()
        self.last_image = (im, time.time() + self.IMAGE_EXPIRE_TIME)

        return self.last_image[0]

# Can be used as a singleton
# In the future, more cameras could be supported

def _load_camera_name() -> str:
    name: str = os.getenv("CAMERA_NAME")
    warning: str | None = "cannot be 'control'" if name == "control" else "is not set" if name is None else None
    if warning:
        print(f"Warning: CAMERA_NAME environment variable {warning}, defaulting to 'camera0'")
        name = "camera0"
    
    return name

CAMERA_NAME = _load_camera_name()
camera_client: CameraClient = CameraClient(CAMERA_NAME)
