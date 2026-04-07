from pydantic import BaseModel
from datetime import datetime

class TimelapseConfig(BaseModel):
    frequency: int  # seconds between captures
    duration:  int  # total duration in seconds
    framerate: int  # frames per second for video assembly
    name: str | None = None

class TimelapseMetadata(BaseModel):
    id: str
    name: str
    frames: int
    framerate: float
    start_date: datetime
    latest_frame_date: datetime | None
    end_date: datetime
    ready: bool

class TimelapseStatus(BaseModel):
    running: bool
    metadata: TimelapseMetadata | None
    config: TimelapseConfig | None = None
