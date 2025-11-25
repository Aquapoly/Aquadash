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

class Measurement(Base):
    __tablename__ = "measurements"

    measurement_id = Column(Integer, primary_key=True)
    sensor_id = Column(
        Integer, ForeignKey("sensors.sensor_id"), nullable=False, index=True
    )
    timestamp = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    value = Column(Float, nullable=False)