import os
from pathlib import Path
import random
import string
from socket import socket, AF_UNIX, SOCK_STREAM
from threading import Thread
import imageio.v3 as iio
from camera_paths import SOCK_DIR

def _random_name(n=8) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

class Camera:
    """Represents a single camera device and its socket server"""
    def __init__(self, camera_dev: str, sock_dir: Path = SOCK_DIR):
        self.camera_dev: str = camera_dev
        self.sock_dir: Path = sock_dir

        self.id: str = _random_name()
        self.sock_path: Path = self.sock_dir / f"{self.id}.sock"
        self.server = socket(AF_UNIX, SOCK_STREAM)
        
        self.server.bind(self.sock_path)
        os.chmod(self.sock_path, 0o660)
        self.server.listen(1)

        self.running = False
        self.thread = Thread(target=self._serve_loop, daemon=True)

    def run(self):
        self.running = True
        self.thread.start()

    def get_frame(self) -> bytes:
        """Capture one frame from the device and return it as PNG bytes."""
        im = iio.imread(self.camera_dev, index=0)
        return iio.imwrite("<bytes>", im, extension=".png")

    def teardown(self):
        self.running = False
        try:
            self.server.close()
        except Exception:
            pass
        try:
            self.sock_path.unlink()
        except FileNotFoundError:
            pass

    def _serve_loop(self):
        """Serve client connections"""
        while self.running:
            try:
                conn, _ = self.server.accept()
                Thread(target=self._handle_client, args=(conn,), daemon=True).start()
            except Exception as e:
                print(f"[Camera {self.camera_dev}] Error: {e}")

    def _handle_client(self, conn: socket):
        try:
            frame = self.get_frame()
            conn.sendall(len(frame).to_bytes(4, "big") + frame)
        except Exception as e:
            print(f"[Camera {self.camera_dev}] Frame error: {e}")
        finally:
            conn.close()