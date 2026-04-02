from pydantic import BaseModel

class TimelapseConfig(BaseModel):
    frequency: int  # seconds between captures
    duration: int   # total duration in seconds
    framerate: int  # frames per second for video assembly

class TimelapseMetadata(BaseModel):
    frames_taken: int
    latest_frame_time: int
    ready: bool
