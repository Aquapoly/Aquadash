from enum import StrEnum, auto

class CameraCommand(StrEnum):
    CREATE = "CREATE_CAMERA"
    REWIRE = "REWIRE_CAMERA"
    REMOVE = "REMOVE_CAMERA"
    LIST = "LIST_CAMERAS"
