# TODO: séparer et déplacer les schemas dans un dossier schema (renommer le dossier "classes")

from pydantic import BaseModel, Field
from datetime import datetime
from .classes.activation_condition import ActivationCondition

from .classes.actuator_type import ActuatorType
from .classes.sensor_type import SensorType



class ActuatorBase(BaseModel):
    actuator_type: ActuatorType
    sensor_id: int
    condition_value: float
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
