
from pydantic import BaseModel
from .models import SensorType

class SensorBase(BaseModel):
    sensor_type: SensorType
    prototype_id: int
    sensor_unit: str
    threshold_critically_low: float
    threshold_low: float
    threshold_high: float
    threshold_critically_high: float


class Sensor(SensorBase):
    sensor_id: int

    class Config:
        from_attributes = True


