from enum import StrEnum, auto

class CameraCommand(StrEnum):
    CREATE = "create"
    REWIRE = "rewire"
    REMOVE = "remove"
    LIST = "list"
    GID = "gid"
