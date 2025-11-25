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


# auth stuff
class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, nullable=False, unique=True)
    pw_salt = Column(String, nullable=False)
    pw_hash = Column(String, nullable=False)
    permissions = Column(Integer, nullable=False)
    logged_in = Column(Boolean, nullable=False)