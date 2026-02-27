import cv2
from threading import Lock

class PhysicalCamera:
    def __init__(self, device_path: str):
        self.device_path = device_path
        self.lock = Lock()
        self.cap = cv2.VideoCapture(device_path, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.count = 0

    def capture_frame(self) -> bytes | None:
        with self.lock:
            # Flush stale frames
            for _ in range(3):
                self.cap.grab()

            ret, frame = self.cap.read()
            if not ret:
                return None

            ret, buf = cv2.imencode(
                ".jpg",
                frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), 85]
            )
            if not ret:
                return None

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
            self.cap.release()