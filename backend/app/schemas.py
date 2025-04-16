# TODO: séparer et déplacer les schemas dans un dossier schema (renommer le dossier "classes")

from pydantic import BaseModel, Field
from datetime import datetime
from .classes.activation_condition import ActivationCondition

from .classes.actuator_type import ActuatorType
from .classes.sensor_type import SensorType
from .classes.notification_type import NotificationType


class Prototype(BaseModel):
    prototype_id: int
    prototype_name: str

    class Config:
        from_attributes = True


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


class MeasurementBase(BaseModel):
    value: float
    sensor_id: int


class Measurement(MeasurementBase):
    measurement_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class ActuatorBase(BaseModel):
    actuator_type: ActuatorType
    sensor_id: int
    low: float
    high: float
    activation_condition: ActivationCondition
    activation_period: float # in seconds
    activation_duration: float # in seconds



class Actuator(ActuatorBase):
    actuator_id: int
    enabled: bool
    last_activated: datetime

    class Config:
        from_attributes = True

class ActuatorActivation(BaseModel):
    activate: bool
    status: str
    duration: float
    period: float

    class Config:
        from_attributes = True

class Picture(BaseModel):
    data: str


# Authentification stuff
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str


class UserInDB(User):
    pw_hash: str
    pw_salt: str
    id: int

class RandomMeasurements(BaseModel):
    nb_measurements:int = 500
    yearly_measurements_ratio:float = 0.80
    dayly_measurements_ratio:float = 0.1
    hourly_measurements_ratio:float = 0.1
    deviation_rate:float = 0.20
    smoothing_factor:float = 0.50
    drift_adjustment:float = 0.15

class NotificationSchema(BaseModel):
    notification_id: int
    timestamp: datetime
    level: NotificationType
    description: str 
    read: bool = Field(default=False)

    class Config:
        from_attributes = True
