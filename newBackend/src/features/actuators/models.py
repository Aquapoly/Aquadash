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

class Actuator(Base):
    __tablename__ = "actuators"
    actuator_id = Column(Integer, primary_key=True)
    actuator_type = Column(Enum(ActuatorType), nullable=False)
    sensor_id = Column(Integer, ForeignKey("sensors.sensor_id"), nullable=False)
    condition_value = Column(Float, nullable=False)
    activation_condition = Column(Enum(ActivationCondition), nullable=False)
    activation_period = Column(Float, nullable=False)
    activation_duration = Column(Float, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    last_activated = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
