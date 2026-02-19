# TODO: séparer et déplacer les schemas dans un dossier schema (renommer le dossier "classes")

from pydantic import BaseModel
from datetime import datetime
class MeasurementBase(BaseModel):
    value: float
    sensor_id: int


class Measurement(MeasurementBase):
    measurement_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class RandomMeasurements(BaseModel):
    nb_measurements:int = 500
    yearly_measurements_ratio:float = 0.80
    dayly_measurements_ratio:float = 0.1
    hourly_measurements_ratio:float = 0.1
    deviation_rate:float = 0.20
    smoothing_factor:float = 0.50
    drift_adjustment:float = 0.15