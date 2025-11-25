from pydantic import BaseModel, Field
from datetime import datetime
from .classes.activation_condition import ActivationCondition

from .classes.actuator_type import ActuatorType
from .classes.sensor_type import SensorType



class Picture(BaseModel):
    data: str