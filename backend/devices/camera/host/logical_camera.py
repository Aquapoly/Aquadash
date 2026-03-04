import os
from pathlib import Path
from socket import socket, AF_UNIX, SOCK_STREAM
from threading import Thread

from physical_camera import PhysicalCamera

class LogicalCamera:
    """Serves frames from a physical camera over a UNIX socket on demand."""
    def __init__(self, logical_name: str, physical_camera: PhysicalCamera, sock_dir: Path):
        self.logical_name = logical_name
        self.physical_camera = physical_camera
        self.sock_dir = sock_dir
        self.sock_path = sock_dir / f"{logical_name}.sock"

        self.server = socket(AF_UNIX, SOCK_STREAM)
        self.server.bind(str(self.sock_path))
        os.chmod(self.sock_path, 0o660)
        self.server.listen(1)

        self.running = False
        self.thread = Thread(target=self._serve_loop, daemon=True)

        self.physical_camera.increase_logical_camera_count()
    
    def reassign_physical_camera(self, physical_camera: PhysicalCamera) -> str:
        old_physical_name: str = self.physical_camera.device_path

        self.physical_camera.decrease_logical_camera_count()
        self.physical_camera = physical_camera
        self.physical_camera.increase_logical_camera_count()

        return old_physical_name

    def run(self):
        self.running = True
        self.thread.start()

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

        self.physical_camera.decrease_logical_camera_count()

    def _serve_loop(self):
        while self.running:
            try:
                conn, _ = self.server.accept()
                Thread(target=self._handle_client, args=(conn,), daemon=True).start()
            except Exception as e:
                print(f"[LogicalCamera {self.logical_name}] Server error: {e}")

    def _handle_client(self, conn: socket):
        try:
            frame = self.physical_camera.capture_frame()
            if frame:
                conn.sendall(len(frame).to_bytes(4, "big") + frame)
        except Exception as e:
            print(f"[LogicalCamera {self.logical_name}] Send error: {e}")
        finally:
            conn.close()

    def __str__(self) -> str:
        return f"{self.logical_name} ---> {self.physical_camera}"