from sqlalchemy import (
    Enum,
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    Time,
    func,
)
import enum
from .classes.activation_condition import ActivationCondition

from .classes.actuator_type import ActuatorType
from .database import Base
from .classes.sensor_type import SensorType


class Prototype(Base):
    __tablename__ = "prototypes"

    prototype_id = Column(Integer, primary_key=True)
    prototype_name = Column(String, nullable=False)