import time
import pytest
from unittest.mock import patch
from ..camera_client import CameraClient, CameraSocketNotFoundError, CameraNotAvailableError

FAKE_FRAME = b'encoded_dummy_image_data'
NEW_FRAME = b'new_image_data'


@pytest.fixture
def camera():
    return CameraClient("test_camera")


def test_get_image_success(camera: CameraClient):
    """Should fetch and cache a new frame when cache is empty."""
    with patch.object(camera, 'capture', return_value=FAKE_FRAME):
        image = camera.get_image()
    assert image == FAKE_FRAME
    assert camera.last_image is not None
    assert camera.last_image[0] == FAKE_FRAME


def test_get_image_uses_unexpired_cache(camera: CameraClient):
    """Should return cached image without calling capture when cache is fresh."""
    camera.last_image = (FAKE_FRAME, time.time() + 10)
    with patch.object(camera, 'capture') as mock_capture:
        image = camera.get_image()
        mock_capture.assert_not_called()
    assert image == FAKE_FRAME


def test_get_image_refreshes_expired_cache(camera: CameraClient):
    """Should fetch a new frame when cache has expired."""
    camera.last_image = (FAKE_FRAME, time.time() - 1)
    with patch.object(camera, 'capture', return_value=NEW_FRAME):
        image = camera.get_image()
    assert image == NEW_FRAME
    assert camera.last_image[0] == NEW_FRAME


def test_get_image_fetch_failure_with_fresh_cache(camera: CameraClient):
    """Should return fresh cached image when capture fails."""
    camera.last_image = (FAKE_FRAME, time.time() + 10)
    with patch.object(camera, 'capture', side_effect=CameraNotAvailableError()):
        image = camera.get_image()
    assert image == FAKE_FRAME


def test_get_image_no_cache_no_camera(camera: CameraClient):
    """Should raise when capture fails and there is no cache at all."""
    camera.last_image = None
    with patch.object(camera, 'capture', side_effect=CameraNotAvailableError()):
        with pytest.raises(CameraNotAvailableError):
            camera.get_image()