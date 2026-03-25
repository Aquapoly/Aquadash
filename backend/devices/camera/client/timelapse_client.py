from datetime import datetime, timezone
from pathlib import Path
import shutil
import threading
import time
import uuid

import imageio.v3 as iio3
from pydantic import BaseModel

from camera_client import CameraClient, CameraSocketNotFoundError, CameraNotAvailableError

TIMELAPSES_DIR = Path("/timelapses")
VIDEO_TEMP_DIR = Path("/tmp/timelapses")


class TimelapseConfig(BaseModel):
    frequency: int  # seconds between captures
    duration: int   # total duration in seconds


class _TimelapseState:
    def __init__(self):
        self.running: bool = False
        self.thread: threading.Thread | None = None
        self.frames_taken: int = 0
        self.latest_frame_time: int | None = None
        self.latest_frame_path: Path | None = None
        self.config: TimelapseConfig | None = None
        self.start_time: float | None = None
        self.id: str | None = None

    def reset(self) -> None:
        self.running = False
        self.thread = None
        self.frames_taken = 0
        self.latest_frame_time = None
        self.latest_frame_path = None
        self.config = None
        self.start_time = None
        self.id = None


class TimelapseClient:
    def __init__(self, camera: CameraClient):
        self._camera: CameraClient = camera
        self._state: _TimelapseState = _TimelapseState()
        self._lock: threading.Lock = threading.Lock()

    def start(self, config: TimelapseConfig) -> dict:
        with self._lock:
            if self._state.running:
                raise ValueError("Timelapse already running")

            self._state.running = True
            self._state.config = config
            self._state.start_time = time.time()
            self._state.id = str(uuid.uuid4())
            self._state.frames_taken = 0
            self._state.latest_frame_time = None
            self._state.latest_frame_path = None
            self._state.thread = threading.Thread(
                target=self._run_worker,
                args=(config, self._state.id),
                daemon=True
            )
            self._state.thread.start()

            return {
                "status": "timelapse started",
                "config": config,
                "timelapse_id": self._state.id,
            }

    def stop(self) -> dict:
        with self._lock:
            if not self._state.running:
                raise ValueError("No timelapse is running")
            self._state.running = False
            thread = self._state.thread

        thread.join(timeout=10.0)
        if thread.is_alive():
            raise RuntimeError("Failed to stop timelapse thread")

        with self._lock:
            self._state.reset()

        return {"status": "timelapse stopped"}

    def status(self) -> dict:
        with self._lock:
            expected_frames = None
            end_time = None
            if self._state.config and self._state.start_time:
                expected_frames = self._state.config.duration // self._state.config.frequency
                end_time = self._state.start_time + self._state.config.duration

            return {
                "running": self._state.running,
                "config": self._state.config.model_dump() if self._state.config else None,
                "frames_taken": self._state.frames_taken,
                "expected_frames": expected_frames,
                "end_time": end_time,
                "latest_frame_time": self._state.latest_frame_time,
                "timelapse_id": self._state.id,
            }

    def get_latest_frame(self) -> Path:
        with self._lock:
            path = self._state.latest_frame_path
        if not path or not path.exists():
            raise FileNotFoundError("No frame available")
        return path

    def list(self) -> list[dict]:
        if not TIMELAPSES_DIR.exists():
            return []

        timelapses = []
        for folder in TIMELAPSES_DIR.iterdir():
            if not folder.is_dir():
                continue
            frames = sorted(folder.glob("frame_*.jpg"))
            if not frames:
                continue
            first_frame_ts = int(frames[0].stem.split("_")[1])
            dt = datetime.fromtimestamp(first_frame_ts, tz=timezone.utc)
            timelapses.append({
                "id": folder.name,
                "date": dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "frames": len(frames),
                "name": f"Timelapse {folder.name[:8]}",
            })

        timelapses.sort(key=lambda x: x["date"], reverse=True)
        return timelapses

    def assemble_video(self, timelapse_id: str) -> Path:
        timelapse_folder: Path = TIMELAPSES_DIR / timelapse_id
        if not timelapse_folder.exists():
            raise FileNotFoundError(f"Timelapse {timelapse_id} not found")

        frames = sorted(timelapse_folder.glob("frame_*.jpg"))
        if not frames:
            raise FileNotFoundError("No frames found for this timelapse")

        VIDEO_TEMP_DIR.mkdir(parents=True, exist_ok=True)
        video_path: Path = VIDEO_TEMP_DIR / f"{timelapse_id}.mp4"

        try:
            with iio3.imopen(str(video_path), "w", plugin="pyav") as writer:
                writer.init_video_stream("libx264", fps=30)
                for frame_path in frames:
                    frame = iio3.imread(frame_path)
                    writer.write_frame(frame)
        except Exception as e:
            video_path.unlink(missing_ok=True)
            raise RuntimeError(f"Video assembly failed: {e}")

        return video_path

    def delete(self, timelapse_id: str) -> dict:
        timelapse_folder: Path = TIMELAPSES_DIR / timelapse_id
        if not timelapse_folder.exists():
            raise FileNotFoundError(f"Timelapse {timelapse_id} not found")
        try:
            shutil.rmtree(timelapse_folder)
            return {"status": "timelapse deleted"}
        except Exception as e:
            raise RuntimeError(f"Failed to delete timelapse: {e}")

    def _capture_frame(self, output_path: Path) -> bool:
        try:
            image_bytes = self._camera._fetch_frame()
            output_path.write_bytes(image_bytes)
            return True
        except (CameraSocketNotFoundError, CameraNotAvailableError, PermissionError) as e:
            print(f"[Timelapse] Frame capture failed: {e}")
            return False

    def _run_worker(self, config: TimelapseConfig, timelapse_id: str) -> None:
        timelapse_folder: Path = TIMELAPSES_DIR / timelapse_id
        timelapse_folder.mkdir(parents=True, exist_ok=True)

        start_time: float = time.time()
        end_time: float = start_time + config.duration
        next_capture: float = start_time

        while True:
            with self._lock:
                if not self._state.running:
                    break

            now: float = time.time()

            if now >= next_capture:
                frame_time: int = int(now)
                frame_path: Path = timelapse_folder / f"frame_{frame_time:010d}.jpg"
                if self._capture_frame(frame_path):
                    with self._lock:
                        self._state.frames_taken += 1
                        self._state.latest_frame_time = frame_time
                        self._state.latest_frame_path = frame_path
                next_capture += config.frequency
            
            if now >= end_time:
                break

            time.sleep(0.1)

        with self._lock:
            self._state.reset()