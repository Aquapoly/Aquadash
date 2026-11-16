# TODO: séparer et déplacer les schemas dans un dossier schema (renommer le dossier "classes")

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from .classes.activation_condition import ActivationCondition, activation_map

from .classes.actuator_type import ActuatorType
from .classes.sensor_type import SensorType


class PartialUpdate(BaseModel):
    """
    Base for PATCH bodies. Fields left out of the request are not modified.
    Fields are optional only so they can be omitted: an explicit null is rejected.
    """

    @field_validator("*", mode="before")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("cannot be null, omit the field to leave it unchanged")
        return value


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


class SensorUpdate(PartialUpdate):
    sensor_type: SensorType | None = None
    prototype_id: int | None = None
    sensor_unit: str | None = None
    threshold_critically_low: float | None = None
    threshold_low: float | None = None
    threshold_high: float | None = None
    threshold_critically_high: float | None = None


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
    condition_value: float
    activation_condition: ActivationCondition
    activation_period: float # in seconds
    activation_duration: float # in seconds



def _supported_activation_condition(condition: ActivationCondition | None):
    # Some conditions exist in the DB enum but have no implementation in activation_map (e.g. low_or_high)
    if condition is not None and condition not in activation_map:
        raise ValueError(f"'{condition.value}' is not a supported activation condition")
    return condition


class ActuatorCreate(ActuatorBase):
    # The check lives here and not in ActuatorBase: Actuator inherits ActuatorBase and is used to
    # serialize responses, which would fail for rows already stored with an unsupported condition.
    _check_condition = field_validator("activation_condition")(_supported_activation_condition)


class Actuator(ActuatorBase):
    actuator_id: int
    enabled: bool
    last_activated: datetime

    class Config:
        from_attributes = True


class ActuatorUpdate(PartialUpdate):
    # last_activated is left out: it has its own route, PATCH /actuators/{actuator_id}/last_activated
    actuator_type: ActuatorType | None = None
    sensor_id: int | None = None
    condition_value: float | None = None
    activation_condition: ActivationCondition | None = None
    activation_period: float | None = None
    activation_duration: float | None = None
    enabled: bool | None = None

    _check_condition = field_validator("activation_condition")(_supported_activation_condition)

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
