from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import threading
import time
import uuid

import imageio.v3 as iio3
from .models import TimelapseConfig, TimelapseMetadata, TimelapseStatus

from camera_client import CameraClient, CameraSocketNotFoundError, CameraNotAvailableError

TIMELAPSES_DIR: Path = Path("/timelapses")


class _TimelapseState:
    def __init__(self):
        self.id: str | None = None
        self.running: bool = False
        self.thread: threading.Thread | None = None

    def reset(self) -> None:
        self.id = None
        self.running = False
        self.thread = None


class TimelapseClient:
    LATEST_FRAME_NAME: str = "latest_frame.jpg"
    METADATA_NAME: str = "metadata.json"

    def __init__(self, camera: CameraClient):
        self._camera: CameraClient = camera
        self._state: _TimelapseState = _TimelapseState()
        self._lock: threading.Lock = threading.Lock()

    def start(self, config: TimelapseConfig) -> TimelapseStatus:
        self._ensure_valid_config(config)

        with self._lock:
            if self._state.running:
                raise ValueError("Timelapse already running")

            self._state.reset()
            self._state.id = str(uuid.uuid4())
            config.name = config.name or f"Timelapse {self._state.id[:8]}"
            self._state.running = True
            self._state.thread = threading.Thread(
                target=self._run_worker,
                args=(config, self._state.id),
                daemon=True
            )
            self._state.thread.start()

        return self.status()

    def _ensure_valid_config(self, config: TimelapseConfig) -> None:
        if config.frequency <= 0:
            raise ValueError("Frequency must be greater than 0")
        if config.duration <= 0:
            raise ValueError("Duration must be greater than 0")
        if config.framerate <= 0:
            raise ValueError("Framerate must be greater than 0")
        if config.duration < config.frequency:
            raise ValueError("Duration must be greater than or equal to frequency")

    def stop(self) -> dict:
        self._stop_worker()

        with self._lock:
            self._state.reset()

        return self.status()

    def status(self) -> TimelapseStatus:
        with self._lock:
            metadata: TimelapseMetadata | None = self._current_metadata() 
        return TimelapseStatus(
            self._state.running,
            metadata,
        )

    def get_latest_frame(self) -> Path:
        with self._lock:
            latest_frame_path: Path = self._latest_frame_path()
            if not latest_frame_path or not latest_frame_path.exists():
                raise FileNotFoundError("No frame available")
            return latest_frame_path

    def list(self) -> list[TimelapseMetadata]:
        if not TIMELAPSES_DIR.exists():
            return []

        timelapses: list[TimelapseMetadata] = []
        for directory in TIMELAPSES_DIR.iterdir():
            if not directory.is_dir():
                continue
            metadata_path: Path = directory / self.METADATA_NAME
            if not metadata_path.exists():
                continue
            timelapses.append(TimelapseMetadata.model_validate_json(metadata_path.read_text()).model_dump())

        timelapses.sort(key=lambda x: x.start_date, reverse=True)
        return timelapses

    def delete(self, timelapse_id: str) -> TimelapseStatus:
        if self._state.running and timelapse_id == self._state.id:
            self._stop_worker()
        timelapse_folder: Path = TIMELAPSES_DIR / timelapse_id
        if not timelapse_folder.exists() or not timelapse_folder.is_dir():
            raise FileNotFoundError(f"Timelapse {timelapse_id} not found")
        shutil.rmtree(timelapse_folder)
        return self.status()

    def _capture_frame(self, output_path: Path) -> bool:
        try:
            image_bytes = self._camera._fetch_frame()
            # atomic write
            tmp = output_path.with_suffix(".tmp")
            try:
                tmp.write_bytes(image_bytes)
                tmp.replace(output_path)
                return True
            except (FileNotFoundError, PermissionError, OSError) as e:
                print(f"[Timelapse] Frame write failed: {e}")
                return False
        except (CameraSocketNotFoundError, CameraNotAvailableError, PermissionError) as e:
            print(f"[Timelapse] Frame capture failed: {e}")
            return False

    def _run_worker(self, config: TimelapseConfig, timelapse_id: str) -> None:
        timelapse_folder: Path = TIMELAPSES_DIR / timelapse_id
        timelapse_folder.mkdir(parents=True, exist_ok=True)

        latest_frame_path: Path = timelapse_folder / self.LATEST_FRAME_NAME

        metadata_path: Path = timelapse_folder / self.METADATA_NAME
        metadata: TimelapseMetadata | None = self._metadata(timelapse_id)
        if (not metadata) or (metadata.id != timelapse_id):
            start_date: datetime = datetime.now(timezone.utc)
            end_date: datetime = start_date + timedelta(seconds=config.duration)
            metadata = TimelapseMetadata(
                id=timelapse_id,
                name=config.name,
                frames=0,
                framerate=config.framerate,
                start_date=start_date,
                latest_frame_date=None,
                end_date=end_date,
                ready=False,
            )
        def dump_metadata():
            # atomic write
            tmp = metadata_path.with_suffix(".tmp")
            try:
                tmp.write_text(metadata.model_dump_json())
                tmp.replace(metadata_path)
            except (FileNotFoundError, PermissionError, OSError) as e:
                print(f"[Timelapse] Metadata write failed: {e}")
                with self._lock:
                    self._state.running = False
        
        video_path: Path = timelapse_folder / "video.mp4"
        video_writer = None
        try:
            video_writer = iio3.imopen(str(video_path), "w", plugin="pyav")
            video_writer.init_video_stream("libx264", fps=config.framerate)
        except Exception as e:
            print(f"[Timelapse] Video writer unavailable: {e}")
        if video_writer is None:
            print("[Timelapse] Error initializing video writer, terminating timelapse")
            with self._lock:
                self._state.running = False
                metadata.ready = None
                dump_metadata()
                return

        def pushback_frame(frame):
            try:
                video_writer.write_frame(frame)
            except Exception as e:
                print(f"[Timelapse] Failed to write frame to video: {e}")
                with self._lock:
                    self._state.running = False

        now: datetime = metadata.start_date
        end_time: datetime = metadata.end_date
        next_capture: datetime = now

        frequency_delta: timedelta = timedelta(seconds=config.frequency)

        while now <= end_time:
            with self._lock:
                if not self._state.running:
                    break

            now = datetime.now(timezone.utc)

            if now >= next_capture:
                try:
                    if self._capture_frame(latest_frame_path):
                        try:
                            frame = iio3.imread(latest_frame_path)
                        except Exception as e:
                            print(f"[Timelapse] Failed to read captured frame: {e}")
                            with self._lock:
                                self._state.running = False
                            break

                        metadata.frames += 1
                        metadata.latest_frame_date = now
                        dump_metadata()
                        pushback_frame(frame)
                except Exception as e:
                    print(f"[Timelapse] Unexpected worker error: {e}")
                    with self._lock:
                        self._state.running = False
                    break

                next_capture += frequency_delta

            time.sleep(0.1)

        if video_writer:
            try:
                video_writer.close()
            except Exception as e:
                print(f"[Timelapse] Error closing video writer: {e}")

        metadata.ready = True
        dump_metadata()

    def _metadata(self, timelapse_id: str) -> TimelapseMetadata | None:
        metadata_path: Path = TIMELAPSES_DIR / timelapse_id / self.METADATA_NAME
        if not metadata_path.exists():
            return None
        return TimelapseMetadata.model_validate_json(metadata_path.read_text())

    def _current_metadata(self) -> TimelapseMetadata | None:
        return self._metadata(self._state.id) if self._state.id else None

    def _latest_frame_path(self) -> Path | None:
        if not self._state.id:
            return None
        return TIMELAPSES_DIR / self._state.id / self.LATEST_FRAME_NAME

    def _stop_worker(self) -> None:
        with self._lock:
            self._state.running = False
            thread = self._state.thread
        if thread:
            thread.join(timeout=5.0)
        if thread and thread.is_alive():
            print("[Timelapse] Warning: Worker thread did not exit cleanly within 5 seconds")
        