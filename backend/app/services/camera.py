import cv2
import os
import glob
import base64
from pathlib import Path
from datetime import datetime

_dir = os.path.join(Path.home(), "camera")

def get_image():
    list_png_files = glob.glob(os.path.join(_dir, "*.png"))
    latest_image = cv2.imread(max(list_png_files, key=os.path.getctime))

    is_sucess, im_buf_arr = cv2.imencode(".png", latest_image)
    byte_im = im_buf_arr.tobytes()

    data = "data:image/png;base64," + base64.b64encode(byte_im).decode()
    picture = {
         "data": data
    }
    return picture
