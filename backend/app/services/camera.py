import imageio.v3 as iio

import time

_last_image: tuple[bytes, float] | None = None
IMAGE_EXPIRE_TIME = 5


def get_image():
    """
    Retrieves the latest camera image, refreshing it if expired.
    Returns:
        bytes: The PNG-encoded image bytes.
    Raises:
        Exception: If image acquisition or encoding fails.
    """

    global _last_image

    if _last_image is not None and _last_image[1] >= time.time():
        return _last_image[0]
    
    im = None
    try:
        im = iio.imread("<video0>", index=0)
        im = iio.imwrite("<bytes>", im, extension=".png")
    except Exception:
        pass

    if im is not None:
        _last_image = (im, time.time() + IMAGE_EXPIRE_TIME)

    if _last_image is None:
        raise OSError("Camera not available")

    return _last_image[0]
