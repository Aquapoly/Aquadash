import io
import time
import pytest
from pathlib import Path
from PIL import Image
from ..camera_client import CameraClient, CameraNotAvailableError
from ..mock_camera import MockCamera, fixed_frames, image_frames
from .. import timelapse_client as timelapse_module
from ..timelapse_client import TimelapseClient, TimelapseConfig

JPEG_MAGIC = b"\xff\xd8"


def test_capture_from_mock(connected_camera: CameraClient, camera_server: MockCamera):
    """A CameraClient should get a JPEG frame from the mock camera."""
    frame = connected_camera.capture()
    assert frame.startswith(JPEG_MAGIC)
    assert camera_server.frames_served == 1


def test_generated_frames_change(connected_camera: CameraClient):
    """Consecutive frames should differ, so that timelapse videos actually have content."""
    assert connected_camera.capture() != connected_camera.capture()


def test_fixed_frames(tmp_path: Path):
    """fixed_frames should serve the exact bytes given, in a loop."""
    with MockCamera(tmp_path / "cam.sock", fixed_frames(b"one", b"two")) as server:
        camera = CameraClient("cam")
        camera.sock_path = server.sock_path
        assert [camera.capture() for _ in range(3)] == [b"one", b"two", b"one"]


def test_image_frames(tmp_path: Path):
    """image_frames should cycle through a directory's images, all at the same size."""
    images = tmp_path / "images"
    images.mkdir()
    Image.new("RGB", (320, 240), "red").save(images / "a.jpg")
    Image.new("RGB", (100, 100), "blue").save(images / "b.png")
    frames = image_frames(images)
    for n in range(2):
        with Image.open(io.BytesIO(frames(n))) as frame:
            assert frame.size == (320, 240)


def test_unavailable_camera(connected_camera: CameraClient, camera_server: MockCamera):
    """An unavailable mock camera should look like an unplugged camera to the client."""
    camera_server.available = False
    with pytest.raises(CameraNotAvailableError):
        connected_camera.capture()
    camera_server.available = True
    assert connected_camera.capture().startswith(JPEG_MAGIC)


def test_stop_removes_socket(tmp_path: Path):
    camera = MockCamera(tmp_path / "cam.sock").start()
    assert camera.sock_path.is_socket()
    camera.stop()
    assert not camera.sock_path.exists()


def test_timelapse_records_video(
    connected_camera: CameraClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """End to end: a short timelapse should capture frames from the mock and produce a video."""
    pytest.importorskip("av", reason="PyAV is only installed in the cam client image")
    monkeypatch.setattr(timelapse_module, "TIMELAPSES_DIR", tmp_path / "timelapses")
    timelapses = TimelapseClient(connected_camera)

    timelapses.start(TimelapseConfig(frequency=1, duration=3, framerate=5, name="mock"))
    deadline = time.monotonic() + 15
    while timelapses.status().running:
        assert time.monotonic() < deadline, "timelapse didn't finish in time"
        time.sleep(0.2)

    [metadata] = timelapses.list()
    assert metadata.ready
    assert metadata.frames >= 2
    video = tmp_path / "timelapses" / metadata.id / TimelapseClient.VIDEO_NAME
    assert video.is_file() and video.stat().st_size > 0
