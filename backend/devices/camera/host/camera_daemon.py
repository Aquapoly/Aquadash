#!/usr/bin/env python3
import os
import time
import signal
from pathlib import Path
from socket import socket, AF_UNIX, SOCK_STREAM
from threading import Thread, Lock
from typing import Dict

from camera_paths import SOCK_DIR, CONTROL_SOCKET
from camera_commands import CameraCommand as Command
from physical_camera import PhysicalCamera
from logical_camera import LogicalCamera

class CameraDaemon:
    """Manages physical and logical cameras with on-demand frame capture."""

    def __init__(self, sock_dir: Path = SOCK_DIR, control_socket_file: Path = CONTROL_SOCKET):
        self.sock_dir = sock_dir
        self.control_socket_file = control_socket_file
        self.lock = Lock()
        self.running = False

        # Maps physical device path -> PhysicalCamera
        self.physical_cameras: Dict[str, PhysicalCamera] = {}
        # Maps logical camera name -> LogicalCamera
        self.logical_cameras: Dict[str, LogicalCamera] = {}

        self.sock_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self.sock_dir, 0o770)

        if control_socket_file.exists():
            control_socket_file.unlink()
        self.control_server = socket(AF_UNIX, SOCK_STREAM)
        self.control_server.bind(str(control_socket_file))
        os.chmod(control_socket_file, 0o660)
        self.control_server.listen(1)

        self.control_thread = Thread(target=self._control_loop, daemon=True)

    def run(self):
        self.running = True
        self.control_thread.start()
        print(f"[Daemon] Control socket listening at {self.control_socket_file}")

    def shutdown(self):
        self.running = False
        with self.lock:
            for cam in self.logical_cameras.values():
                cam.teardown()
            for cam in self.physical_cameras.values():
                cam.shutdown()
            self.logical_cameras.clear()
            self.physical_cameras.clear()
        try:
            self.control_server.close()
            self.control_socket_file.unlink()
        except Exception:
            pass
        print("[Daemon] Shutdown complete")

    # --------------------------
    # Control socket
    # --------------------------
    def _control_loop(self):
        while self.running:
            try:
                conn, _ = self.control_server.accept()
                Thread(target=self._handle_control_conn, args=(conn,), daemon=True).start()
            except Exception as e:
                print(f"[Daemon] Control accept error: {e}")

    def _handle_control_conn(self, conn: socket):
        try:
            data = conn.recv(1024).decode().strip()
            if not data:
                return
            parts = data.split(maxsplit=2)
            cmd = parts[0]
            arg0 = parts[1] if len(parts) > 1 else None
            arg1 = parts[2] if len(parts) > 2 else None
            response = ""

            with self.lock:
                match cmd:
                    case Command.CREATE:
                        if not arg0:
                            response = "Missing logical camera name"
                        else:
                            logical_name: str = arg0
                            phys_dev: str = arg1 or logical_name
                            response = self._create_logical_camera(logical_name, phys_dev)

                    case Command.REWIRE:
                        if not arg0 or not arg1:
                            response = "rewire requires logical_name and new_physical_device"
                        else:
                            logical_name: str = arg0
                            phys_dev: str = arg1
                            response = self._rewire_logical_camera(logical_name, phys_dev)

                    case Command.REMOVE:
                        if not arg0:
                            response = "remove requires logical camera name"
                        else:
                            logical_name: str = arg0
                            response = self._remove_logical_camera(logical_name)

                    case Command.LIST:
                        response = self._get_list()

                    case Command.GID:
                        response = self._get_gid()

                    case _:
                        response = f"Unknown command: {cmd}"

            conn.sendall(response.encode())
        finally:
            conn.close()
    
    def _get_or_create_physical_camera(self, phys_dev: str) -> PhysicalCamera:
        if phys_dev in self.physical_cameras:
            return self.physical_cameras[phys_dev]

        phys_cam = PhysicalCamera(phys_dev)
        self.physical_cameras[phys_dev] = phys_cam
        return phys_cam
    
    def _create_logical_camera(self, logical_name: str, phys_dev: str) -> str:
        if logical_name in self.logical_cameras:
            return f"Logical camera {logical_name} already exists"

        phys_cam: PhysicalCamera = self._get_or_create_physical_camera(phys_dev)

        log_cam = LogicalCamera(logical_name, phys_cam, sock_dir=self.sock_dir)
        self.logical_cameras[logical_name] = log_cam
        log_cam.run()
        return f"Logical camera created: {log_cam}"

    def _destroy_physical_camera_if_dangling(self, phys_dev: str) -> None:
        phys_cam: PhysicalCamera = self.physical_cameras.get(phys_dev)
        if not phys_cam:
            return

        if phys_cam.empty():
            phys_cam.shutdown()
            self.physical_cameras.pop(phys_dev)
    
    def _rewire_logical_camera(self, logical_name: str, phys_dev: str) -> str:
        log_cam: LogicalCamera = self.logical_cameras.get(logical_name)
        if not log_cam:
            return f"Logical camera {arg0} does not exist"

        new_phys_cam: PhysicalCamera = self._get_or_create_physical_camera(phys_dev)
        old_phys_dev: str = log_cam.reassign_physical_camera(new_phys_cam)

        self._destroy_physical_camera_if_dangling(old_phys_dev)

        return f"Logical camera {logical_name} rewired to {phys_dev} (was {old_phys_dev})"

    def _remove_logical_camera(self, logical_name: str) -> str:
        log_cam: LogicalCamera = self.logical_cameras.pop(logical_name)
        if not log_cam:
            return f"Logical camera {arg0} does not exist"
        phys_dev: str = log_cam.physical_camera.device_path
        log_cam.teardown()

        self._destroy_physical_camera_if_dangling(phys_dev)

        return f"Logical camera {logical_name} removed"

    def _get_list(self) -> str:
        return "\n".join(str(cam) for cam in self.logical_cameras.values())

    def _get_gid(self) -> str:
        import grp
        try:
            return str(grp.getgrnam("host-dev").gr_gid)
        except KeyError:
            return "host-dev group not found"


if __name__ == "__main__":
    daemon = CameraDaemon()

    def shutdown_handler(signum, frame):
        print("[Daemon] Signal received, shutting down...")
        daemon.shutdown()
        exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    daemon.run()
    print("[Daemon] Running. Use control socket to CREATE/REWIRE/REMOVE/LIST cameras.")

    while daemon.running:
        time.sleep(1)