import pytest
from app.services import camera
import time

FAKE_FRAME = b'encoded_dummy_image_data'


def fetch_frame_success():
    return FAKE_FRAME


def fetch_frame_failure():
    raise OSError("No camera available")


# Test get_image
def test_get_image_success(monkeypatch):
    monkeypatch.setattr(camera, "_fetch_frame", fetch_frame_success)

    camera._last_image = None
    image = camera.get_image()
    
    assert image == fetch_frame_success(), "Should return the fetched frame"
    assert camera._last_image is not None, "Should cache the new image"


def test_get_image_fetch_failure_with_cache(monkeypatch):
    monkeypatch.setattr(camera, "_fetch_frame", fetch_frame_failure)

    camera._last_image = (FAKE_FRAME, time.time() + camera.IMAGE_EXPIRE_TIME)
    image = camera.get_image()

    assert image == FAKE_FRAME, "Should return cached image when fetch fails"
    assert camera._last_image[0] == FAKE_FRAME, "Should not replace cache when fetch fails"


def test_get_image_no_cache_no_camera(monkeypatch):
    monkeypatch.setattr(camera, "_fetch_frame", fetch_frame_failure)

    camera._last_image = None
    with pytest.raises(OSError):
        camera.get_image()


def test_get_image_expired(monkeypatch):
    monkeypatch.setattr(camera, "_fetch_frame", fetch_frame_success)

    camera._last_image = (fetch_frame_success(), time.time() - 10)
    image = camera.get_image()

    assert image == fetch_frame_success(), "Should return a new image if the last image is expired"
    assert camera._last_image[0] == fetch_frame_success(), "Should update cache when expired"


def test_get_image_expired_fetch_failure(monkeypatch):
    monkeypatch.setattr(camera, "_fetch_frame", fetch_frame_failure)

    camera._last_image = (FAKE_FRAME, time.time() - 10)
    image = camera.get_image()

    assert image == FAKE_FRAME, "Should return stale cache when fetch fails after expiry"
    assert camera._last_image[0] == FAKE_FRAME, "Should not replace cache when fetch fails"