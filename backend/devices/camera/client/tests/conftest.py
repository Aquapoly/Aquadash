import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..camera_client import CameraClient

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_camera():
    """Returns a CameraClient with a mocked capture method."""
    cam = CameraClient("test_camera")
    return cam