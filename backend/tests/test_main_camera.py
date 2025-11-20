from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.services import camera
from app.services.camera import IMAGE_EXPIRE_TIME
import time

# Mocks
def mock_get_image_success(*args, **kwargs):
    new_image = b'plant image'
    camera._last_image = (new_image, time.time() + IMAGE_EXPIRE_TIME)
    return new_image


def mock_get_image_unexpired(*args, **kwargs):
    return camera._last_image[0]


# imread with <video0> uses the PyAv plugin, which can raise OSError if no camera is found at the specified URI
def mock_get_image_error(*args, **kwargs):
    raise OSError("Device not found")


# GET /picture
def test_get_picture_success(client: TestClient, monkeypatch, set_last_image):
    """Test /picture endpoint to internally update the last image"""
    monkeypatch.setattr(camera, "get_image", mock_get_image_success)

    response = client.get("/picture")
    assert response.status_code == 200, f"Should return 200 for successful operation, got {response.status_code}"
    assert camera._last_image[0] == b'plant image', "Should update image"


def test_get_picture_unexpired(client: TestClient, monkeypatch, set_last_image):
    """Test /picture endpoint when the last image hasn't expired"""
    monkeypatch.setattr(camera, "get_image", mock_get_image_unexpired)

    response = client.get("/picture")
    assert response.status_code == 200, f"Should return 200 for successful operation, got {response.status_code}"


def test_get_picture_error(client: TestClient, monkeypatch, set_last_image):
    """Test /picture endpoint when there is no camera"""
    monkeypatch.setattr(camera, "get_image", mock_get_image_error)
    
    response = client.get("/picture")
    assert response.status_code == 503, f"Should return 503 for no camera found, got {response.status_code}"