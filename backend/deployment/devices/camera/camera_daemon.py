#!/usr/bin/env python3
import os
from pathlib import Path
from socket import socket, AF_UNIX, SOCK_STREAM
from threading import Thread, Lock
from typing import Dict
import time

from camera_paths import SOCK_DIR, CURRENT_DIR, CONTROL_SOCKET
from camera_commands import CameraCommand as Command
from camera import Camera

class CameraDaemon:
    """Manages multiple cameras and a control socket"""
    
    def __init__(
            self,
            sock_dir: Path=SOCK_DIR,
            current_dir: Path=CURRENT_DIR,
            control_socket_file: Path=CONTROL_SOCKET
    ):
        """
        Args:
            sock_dir: runtime directory where camera sockets are created
            current_dir: directory where symlinks to cameras are created for discovery
            cameras: mapping of camera device paths to Camera instances
            control_socket: path to the control socket for managing cameras
        """

        self.sock_dir: Path = sock_dir
        self.sock_dir.mkdir(mode=0o750, exist_ok=True)  # normally created by systemd

        self.current_dir: Path = current_dir
        self.current_dir.mkdir(mode=0o750, exist_ok=True)

        self.cameras: Dict[str, Camera] = {}   # device path -> Camera
        self.lock: Lock = Lock()
        
        self.control_socket_file: Path = control_socket_file
        if control_socket_file.exists():
            control_socket_file.unlink()

        self.control_server: socket = socket(AF_UNIX, SOCK_STREAM)
        self.control_server.bind(control_socket_file)
        os.chmod(control_socket_file, 0o660)
        self.control_server.listen(1)

        self.running: bool = False
        self.control_thread: Thread = Thread(target=self._control_loop, daemon=True)

    def run(self):
        self.running = True
        self.control_thread.start()
        print(f"[Daemon] Control socket listening at {self.control_socket_file}")

    def _control_loop(self):
        while self.running:
            try:
                conn, _ = self.control_server.accept()
                t: Thread = Thread(target=self._handle_control_conn, args=(conn,), daemon=True)
                t.start()
            except Exception as e:
                print(f"[Daemon] Control accept error: {e}")

    def _handle_control_conn(self, conn: socket):
        try:
            data: str = conn.recv(1024).decode().strip()
            if not data:
                return
            
            parts: str = data.split(maxsplit=1)
            cmd: str = (parts[0].upper())
            arg: str = parts[1] if len(parts) > 1 else ""
            response: str = ""

            match cmd:
                case Command.ADD:
                    cam = self.expose_new_camera(arg)
                    response = f"Camera added: {cam.camera_dev} -> {cam.sock_path}"

                case Command.REMOVE:
                    self.remove_camera(arg)
                    response = f"Camera removed: {arg}"

                case Command.LIST:
                    with self.lock:
                        response = "\n".join(self.cameras.keys())

                case Command.SHUTDOWN:
                    response = "Daemon shutting down"
                    self.shutdown()

                case _:
                    response = f"Unknown command: {cmd}"

            conn.sendall(response.encode())

        finally:
            conn.close()

    def expose_new_camera(self, camera_dev_file: Path) -> Camera:
        with self.lock:
            if camera_dev_file in self.cameras:
                return self.cameras[camera_dev_file]

            cam: Camera = Camera(camera_dev_file, sock_dir=self.sock_dir)
            cam.run()
            self.cameras[camera_dev_file] = cam

            # symlink for discovery
            symlink_path: Path = self.current_dir / camera_dev_file.name
            try:
                if os.path.exists(symlink_path):
                    os.remove(symlink_path)
                os.symlink(cam.sock_path, symlink_path)
            except Exception as e:
                print(f"[Daemon] Failed to create symlink for {camera_dev_file}: {e}")

            return cam

    def remove_camera(self, camera_dev: Path):
        with self.lock:
            cam: Camera | None = self.cameras.pop(camera_dev, None)
            if not cam:
                return
            
            cam.teardown()
            symlink_path = self.current_dir / camera_dev.name

            try:
                symlink_path.unlink()
            except FileNotFoundError:
                pass

    def shutdown(self):
        self.running = False
        with self.lock:
            for cam in list(self.cameras.values()):
                cam.teardown()
            self.cameras.clear()

        try:
            for f in self.current_dir.iterdir():
                f.unlink()
        except Exception:
            pass

        try:
            self.control_server.close()
            os.remove(self.control_socket_file)
        except Exception:
            pass

        print("[Daemon] Shutdown complete")


if __name__ == "__main__":
    daemon = CameraDaemon()

    def shutdown_handler(signum, frame):
        print("[Daemon] Signal received, shutting down...")
        daemon.shutdown()
        exit(0)

    from signal import signal, SIGINT, SIGTERM

    signal(SIGINT, shutdown_handler)
    signal(SIGTERM, shutdown_handler)

    daemon.run()

    print("[Daemon] Running. Use control socket to ADD/REMOVE cameras, LIST_CAMERAS, or SHUTDOWN.")

    # main thread just sleeps
    while daemon.running:
        time.sleep(1)
