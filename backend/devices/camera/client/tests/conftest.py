from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..camera_client import CameraClient
from ..mock_camera import MockCamera

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_camera():
    """Returns a CameraClient with a mocked capture method."""
    cam = CameraClient("test_camera")
    return cam

@pytest.fixture
def camera_server(tmp_path: Path):
    """A mock camera daemon serving generated frames on a temporary socket."""
    with MockCamera(tmp_path / "camera0.sock") as server:
        yield server


@pytest.fixture
def connected_camera(camera_server: MockCamera) -> CameraClient:
    """A CameraClient connected to `camera_server`."""
    camera = CameraClient("camera0")
    camera.sock_path = camera_server.sock_path
    return camera
