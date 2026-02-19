import cv2
import os
import glob
from pathlib import Path
from datetime import datetime

_dir = os.path.join(Path.home(), "camera")
MAX_IMAGES = 5

def save_image():
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        print("Could not open video device")
        return

    os.makedirs(_dir, exist_ok=True)
    path = os.path.join(_dir, str(datetime.now()) + ".png")

    filescount = len(os.listdir(_dir))
    if filescount >= MAX_IMAGES:
        list_of_files = glob.glob(os.path.join(_dir, "*"))
        oldest_file = min(list_of_files, key=os.path.getctime)
        os.remove(oldest_file)

    ret, frame = capture.read()

    cv2.imwrite(path, frame)
    cv2.waitKey(0)

    del(capture)

if __name__ == "__main__":
    save_image()
