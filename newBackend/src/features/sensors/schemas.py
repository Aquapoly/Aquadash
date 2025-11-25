# TODO: séparer et déplacer les schemas dans un dossier schema (renommer le dossier "classes")

from pydantic import BaseModel
from src.enums.sensor_type import SensorType



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
