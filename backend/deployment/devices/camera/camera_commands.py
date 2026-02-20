from enum import StrEnum, auto

class CameraCommand(StrEnum):
    ADD = "ADD_CAMERA"
    REMOVE = "REMOVE_CAMERA"
    LIST = "LIST_CAMERAS"
    SHUTDOWN = "SHUTDOWN"
