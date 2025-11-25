# TODO: séparer et déplacer les schemas dans un dossier schema (renommer le dossier "classes")

from pydantic import BaseModel, Field
from datetime import datetime
from .classes.activation_condition import ActivationCondition

from .classes.actuator_type import ActuatorType
from .classes.sensor_type import SensorType


class Prototype(BaseModel):
    prototype_id: int
    prototype_name: str

    class Config:
        from_attributes = True