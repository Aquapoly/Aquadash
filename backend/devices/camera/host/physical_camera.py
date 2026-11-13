import cv2
from threading import Lock

class PhysicalCamera:
    def __init__(self, device_path: str):
        self.device_path = device_path
        self.lock = Lock()
        self.cap: cv2.VideoCapture | None = None
        self.failing = False
        self.count = 0
        with self.lock:
            self._open()

    def _open(self) -> None:
        self.cap = cv2.VideoCapture(self.device_path, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def _release(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def _fail(self, reason: str) -> None:
        # A failed capture can leave OpenCV's V4L2 state unusable, so
        # release the device and reopen on the next request.
        self._release()
        if not self.failing:
            print(f"[PhysicalCamera {self.device_path}] Capture failed: {reason}. Will reopen on next request.")
        self.failing = True

    def capture_frame(self) -> bytes | None:
        with self.lock:
            if self.cap is None or not self.cap.isOpened():
                self._release()
                self._open()
                if not self.cap.isOpened():
                    self._fail("could not open device")
                    return None

            # Flush stale frame
            self.cap.grab()

            ret, frame = self.cap.read()
            if not ret:
                self._fail("could not read frame")
                return None

            ret, buf = cv2.imencode(
                ".jpg",
                frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), 85]
            )
            if not ret:
                self._fail("could not encode frame")
                return None

            if self.failing:
                print(f"[PhysicalCamera {self.device_path}] Capture recovered")
                self.failing = False

            return buf.tobytes()

    def increase_logical_camera_count(self):
        self.count += 1

    def decrease_logical_camera_count(self):
        self.count -= 1
        if self.count <= 0:
            self.count = 0

    def empty(self) -> bool:
        return self.count == 0

    def __str__(self) -> str:
        return self.device_path

    def shutdown(self):
        with self.lock:
            self._release()
