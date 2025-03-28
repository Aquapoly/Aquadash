import imageio.v3 as iio

import time

_last_image = None
IMAGE_EXPIRE_TIME = 5


def get_image():
    global _last_image
    if _last_image is None or _last_image[1] < time.time():
        im = iio.imread("<video0>", index=0)
        im = iio.imwrite("<bytes>", im, extension=".png")
        _last_image = (im, time.time() + IMAGE_EXPIRE_TIME)

    return _last_image[0]
