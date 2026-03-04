import time
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from ..camera_client import CameraClient, CameraSocketNotFoundError, CameraNotAvailableError

FAKE_IMAGE = b'plant image'


@pytest.fixture
def camera():
    return CameraClient("test_camera")


def test_get_picture_success(client: TestClient):
    """Test /picture returns 200 with image bytes on success."""
    with patch.object(CameraClient, 'get_image', return_value=FAKE_IMAGE):
        response = client.get("/picture")
    assert response.status_code == 200
    assert response.content == FAKE_IMAGE


def test_get_picture_uses_cache(camera: CameraClient):
    """Test that get_image returns cached image before expiry."""
    camera.last_image = (FAKE_IMAGE, time.time() + 10)
    with patch.object(camera, 'capture') as mock_capture:
        result = camera.get_image()
        mock_capture.assert_not_called()
    assert result == FAKE_IMAGE


def test_get_picture_refreshes_expired_cache(camera: CameraClient):
    """Test that get_image fetches a new frame when cache is expired."""
    camera.last_image = (b'old image', time.time() - 1)
    with patch.object(camera, 'capture', return_value=FAKE_IMAGE):
        result = camera.get_image()
    assert result == FAKE_IMAGE


def test_get_picture_socket_not_found(client: TestClient):
    """Test /picture returns 503 when socket is missing."""
    with patch.object(CameraClient, 'get_image', side_effect=CameraSocketNotFoundError("no socket")):
        response = client.get("/picture")
    assert response.status_code == 503


def test_get_picture_camera_unavailable(client: TestClient):
    """Test /picture returns 404 when camera is unavailable."""
    with patch.object(CameraClient, 'get_image', side_effect=CameraNotAvailableError("no camera")):
        response = client.get("/picture")
    assert response.status_code == 404


def test_get_picture_permission_error(client: TestClient):
    """Test /picture returns 503 on permission error."""
    with patch.object(CameraClient, 'get_image', side_effect=PermissionError("denied")):
        response = client.get("/picture")
    assert response.status_code == 503