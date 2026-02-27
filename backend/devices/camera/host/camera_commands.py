from enum import StrEnum

class CameraCommand(StrEnum):
    CREATE = "create"
    REWIRE = "rewire"
    REMOVE = "remove"
    LIST = "list"
    GID = "gid"
