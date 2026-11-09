"""Mock camera daemon, for development and tests without a physical camera.

It serves the same protocol as the host's `camera-daemon` on a Unix socket:
for each connection, a 4-byte big-endian length, then one JPEG frame.

As a script (see `./run cam --mock`):

    python mock_camera.py --name camera0 [--images DIR] [--size 640x480]

In tests:

    with MockCamera(tmp_path / "camera0.sock") as camera:
        CameraClient(...).capture()
"""
from __future__ import annotations

import argparse
import io
import itertools
import os
import random
import socket
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator

from PIL import Image, ImageDraw

FrameSource = Callable[[int], bytes]
"""Returns the JPEG bytes of the n-th frame served."""

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def generated_frames(width: int = 640, height: int = 480) -> FrameSource:
    """Frames that change every time (moving bar, timestamp, noise), so timelapse videos keep growing."""
    def frame(n: int) -> bytes:
        image = Image.new("RGB", (width, height), (20, 60 + n * 7 % 120, 40))
        draw = ImageDraw.Draw(image)
        x = (n * 37) % width
        draw.rectangle([x, 0, x + width // 10, height], fill=(200, 180, 60))
        for _ in range(width * height // 750):  # some noise, so frames don't compress to nothing
            draw.point((random.randrange(width), random.randrange(height)), fill=(random.randrange(256),) * 3)
        draw.text((20, 20), f"MOCK CAMERA  #{n}", fill=(255, 255, 255))
        draw.text((20, 40), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fill=(255, 255, 255))
        return _to_jpeg(image)
    return frame


def image_frames(directory: Path, width: int | None = None, height: int | None = None) -> FrameSource:
    """Cycles through the images in a directory, in name order (e.g. real photos of the setup)."""
    paths = sorted(p for p in directory.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS)
    if not paths:
        raise ValueError(f"No images found in {directory}")
    # Every frame must have the same size, or the video writer rejects it
    size = (width, height) if width and height else Image.open(paths[0]).size

    def frame(n: int) -> bytes:
        image = Image.open(paths[n % len(paths)]).convert("RGB")
        if image.size != size:
            image = image.resize(size)
        return _to_jpeg(image)
    return frame


def fixed_frames(*frames: bytes) -> FrameSource:
    """Serves the given bytes as-is, in a loop. Useful to assert on exact content in tests."""
    cycle: Iterator[bytes] = itertools.cycle(frames)
    return lambda n: next(cycle)


def _to_jpeg(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    return buffer.getvalue()


class MockCamera:
    """Serves frames on a Unix socket, in a background thread.

    Set `available = False` to simulate a camera that is unplugged: connections
    get closed without a frame, which `CameraClient` reports as
    `CameraNotAvailableError`.
    """

    def __init__(self, sock_path: Path, frames: FrameSource | None = None, mode: int = 0o660):
        self.sock_path = Path(sock_path)
        self.frames: FrameSource = frames or generated_frames()
        self.mode = mode
        self.available: bool = True
        self.frames_served: int = 0
        self._server: socket.socket | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> MockCamera:
        self.sock_path.parent.mkdir(parents=True, exist_ok=True)
        self.sock_path.unlink(missing_ok=True)
        self._server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server.bind(str(self.sock_path))
        os.chmod(self.sock_path, self.mode)
        self._server.listen()
        self._thread = threading.Thread(target=self._serve, name="mock-camera", daemon=True)
        self._thread.start()
        return self

    def stop(self) -> None:
        if self._server is not None:
            # shutdown() wakes up the blocking accept() in the serving thread
            try:
                self._server.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self._server.close()
            self._server = None
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None
        self.sock_path.unlink(missing_ok=True)

    def wait(self) -> None:
        """Blocks until the camera is stopped (or forever, when run as a script)."""
        if self._thread is not None:
            self._thread.join()

    def __enter__(self) -> MockCamera:
        return self.start()

    def __exit__(self, *_) -> None:
        self.stop()

    def _serve(self) -> None:
        assert self._server is not None
        while True:
            try:
                conn, _ = self._server.accept()
            except OSError:
                return  # stopped
            with conn:
                if not self.available:
                    continue
                frame = self.frames(self.frames_served)
                try:
                    conn.sendall(len(frame).to_bytes(4, "big") + frame)
                except OSError:
                    continue  # client went away
                self.frames_served += 1


def _parse_size(value: str) -> tuple[int, int]:
    width, _, height = value.lower().partition("x")
    return int(width), int(height)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--name", default=os.getenv("CAMERA_NAME", "camera0"), help="logical camera name (default: $CAMERA_NAME or camera0)")
    parser.add_argument("--sock-dir", type=Path, default=Path("/run/camera"), help="directory of the socket (default: /run/camera)")
    parser.add_argument("--images", type=Path, help="serve the images in this directory instead of generated frames")
    parser.add_argument("--size", type=_parse_size, help="frame size, e.g. 640x480 (default: 640x480, or the first image's size)")
    parser.add_argument("--mode", type=lambda v: int(v, 8), default=0o660, help="socket permissions, in octal (default: 660)")
    args = parser.parse_args()

    width, height = args.size or (None, None)
    if args.images:
        frames = image_frames(args.images, width, height)
    else:
        frames = generated_frames(width or 640, height or 480)

    camera = MockCamera(args.sock_dir / f"{args.name}.sock", frames, mode=args.mode).start()
    print(f"[Mock camera] Serving frames on {camera.sock_path}", flush=True)
    try:
        camera.wait()
    except KeyboardInterrupt:
        pass
    finally:
        camera.stop()


if __name__ == "__main__":
    main()
