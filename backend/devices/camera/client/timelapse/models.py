from pydantic import BaseModel
from datetime import datetime

class TimelapseConfig(BaseModel):
    frequency: int  # seconds between captures
    duration:  int  # total duration in seconds
    framerate: int  # frames per second for video assembly

class TimelapseMetadata(BaseModel):
    id: str
    name: str
    frames: int
    framerate: float
    start_date: datetime
    last_frame_date: datetime
    end_date: datetime
    ready: bool
