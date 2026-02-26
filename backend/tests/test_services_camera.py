import pytest
import imageio.v3 as iio
from app.services import camera
import time

# Mock functions
def mock_iio_imread_success(*args, **kwargs):
    return b'dummy_image_data'


def mock_iio_imwrite_success(*args, **kwargs):
    return b'encoded_dummy_image_data'


def mock_iio_imread_failure(*args, **kwargs):
    return None


def mock_iio_imwrite_failure(*args, **kwargs):
    return None


# Test get_image
def test_get_image_success(monkeypatch):
    monkeypatch.setattr(iio, "imread", mock_iio_imread_success)
    monkeypatch.setattr(iio, "imwrite", mock_iio_imwrite_success)

    camera._last_image = None
    image = camera.get_image()
    
    assert image == mock_iio_imwrite_success(), "Should return the encoded image data"
    assert camera._last_image is not None, "Should replace the last image with the new one"


@pytest.mark.parametrize("last_image", [None, mock_iio_imwrite_success()])
def test_get_image_read_failure(monkeypatch, last_image):
    monkeypatch.setattr(iio, "imread", mock_iio_imread_failure)

    camera._last_image = (last_image, camera._last_image[1])
    image = camera.get_image()

    assert image == last_image, "Should not return another image than the last image if read fails"
    assert camera._last_image[0] == last_image, "Should not replace the last image if read fails"


@pytest.mark.parametrize("last_image", [None, mock_iio_imwrite_success()])
def test_get_image_write_failure(monkeypatch, last_image):
    monkeypatch.setattr(iio, "imread", mock_iio_imread_success)
    monkeypatch.setattr(iio, "imwrite", mock_iio_imwrite_failure)

    camera._last_image = (last_image, camera._last_image[1])
    image = camera.get_image()

    assert image == last_image, "Should not return another image than the last image if write fails"
    assert camera._last_image[0] == last_image, "Should not replace the last image if write fails"


def test_get_image_expired(monkeypatch):
    monkeypatch.setattr(iio, "imread", mock_iio_imread_success)
    monkeypatch.setattr(iio, "imwrite", mock_iio_imwrite_success)

    camera._last_image = (mock_iio_imwrite_success(), time.time() - 10)
    image = camera.get_image()

    assert image == mock_iio_imwrite_success(), "Should return a new image if the last image is expired"
    assert camera._last_image[0] == mock_iio_imwrite_success(), "Should replace the last image if it's expired"


def test_get_image_expired_read_failure(monkeypatch):
    monkeypatch.setattr(iio, "imread", mock_iio_imread_failure)

    camera._last_image = (mock_iio_imwrite_success(), time.time() - 10)
    last_image = camera._last_image
    image = camera.get_image()

    assert image == last_image[0], "Should not return a new image if it cannot read a new image"
    assert camera._last_image[0] == mock_iio_imwrite_success(), "Should not replace the last image if it cannot read a new image"


def test_get_image_expired_write_failure(monkeypatch):
    monkeypatch.setattr(iio, "imread", mock_iio_imread_success)
    monkeypatch.setattr(iio, "imwrite", mock_iio_imwrite_failure)

    camera._last_image = (mock_iio_imwrite_success(), time.time() - 10)
    last_image = camera._last_image
    image = camera.get_image()

    assert image == last_image[0], "Should not return a new image if it cannot read a new image"
    assert camera._last_image[0] == mock_iio_imwrite_success(), "Should not replace the last image if it cannot read a new image"