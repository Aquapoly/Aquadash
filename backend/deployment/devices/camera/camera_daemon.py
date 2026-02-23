#!/usr/bin/env python3
import os
from pathlib import Path
from socket import socket, AF_UNIX, SOCK_STREAM
from threading import Thread, Lock
from typing import Dict
import time

from camera_paths import SOCK_DIR, CONTROL_SOCKET
from camera_commands import CameraCommand as Command
from camera import Camera

class CameraDaemon:
    """Manages multiple cameras and a control socket"""
    
    def __init__(
            self,
            sock_dir: Path=SOCK_DIR,
            control_socket_file: Path=CONTROL_SOCKET
    ):
        """
        Args:
            sock_dir: runtime directory where camera sockets are created
            cameras: mapping of camera device paths to Camera instances
            control_socket: path to the control socket for managing cameras
        """

        self.sock_dir: Path = sock_dir
        self.sock_dir.mkdir(mode=0o750, exist_ok=True)  # normally created by systemd

        self.cameras: Dict[str, Camera] = {}   # logical name -> Camera
        self.lock: Lock = Lock()
        
        self.control_socket_file: Path = control_socket_file
        if control_socket_file.exists():
            control_socket_file.unlink()

        self.control_server: socket = socket(AF_UNIX, SOCK_STREAM)
        self.control_server.bind(str(control_socket_file))
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
            
            parts: list[str] = data.split(maxsplit=2)
            cmd: str = parts[0].upper()
            arg0: str | None = parts[1] if len(parts) > 1 else None
            arg1: str | None = parts[2] if len(parts) > 2 else None
            response: str = ""

            match cmd:
                case Command.CREATE:
                    # CREATE supports 1 arg (device) or 2 args (name device)
                    if arg1:  # 2 args: name device
                        cam = self.create_camera(arg1, logical_name=arg0)
                    else:  # 1 arg: device only
                        cam = self.create_camera(arg0)
                    response = f"Camera added: {cam.logical_name} ({cam.camera_dev}) -> {cam.sock_path}"

                case Command.REWIRE:
                    self.rewire_camera(arg0, arg1)
                    response = f"Camera rewired: {arg0} -> {arg1}"

                case Command.REMOVE:
                    self.remove_camera(arg0)
                    response = f"Camera removed: {arg0}"

                case Command.LIST:
                    with self.lock:
                        response = "\n".join(self.cameras.keys())

                case _:
                    response = f"Unknown command: {cmd}"

            conn.sendall(response.encode())

        finally:
            conn.close()
    
    def create_camera(self, camera_dev_file: str, logical_name: str | None = None) -> Camera:
        with self.lock:
            cam: Camera = Camera(camera_dev_file, logical_name, sock_dir=self.sock_dir)
            logical_name = cam.logical_name

            if logical_name in self.cameras:
                print(f"[Daemon] Camera {logical_name} already exists")
                return self.cameras[logical_name]
            
            self.cameras[cam.logical_name] = cam
            cam.run()
            return cam
    
    def rewire_camera(self, logical_name: str, new_camera_dev_file: str):
        with self.lock:
            if logical_name not in self.cameras:
                raise ValueError(f"Camera {logical_name} does not exist")
            
            self.cameras[logical_name].rewire(new_camera_dev_file)

    def remove_camera(self, logical_name: str):
        with self.lock:
            cam: Camera | None = self.cameras.pop(logical_name, None)
            if not cam:
                raise ValueError(f"Camera {logical_name} does not exist")
            
            cam.teardown()

    def shutdown(self):
        self.running = False
        with self.lock:
            for cam in list(self.cameras.values()):
                cam.teardown()
            self.cameras.clear()

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

    print("[Daemon] Running. Use control socket to CREATE/REWIRE/REMOVE/LIST cameras.")

    # main thread just sleeps
    while daemon.running:
        time.sleep(1)
