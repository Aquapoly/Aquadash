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

class Sensor(Base):
    __tablename__ = "sensors"

    sensor_id = Column(Integer, primary_key=True)
    sensor_type = Column(Enum(SensorType), nullable=False)
    prototype_id = Column(
        Integer, ForeignKey("prototypes.prototype_id"), nullable=False
    )
    threshold_critically_low = Column(Float, nullable=False)
    threshold_low = Column(Float, nullable=False)
    threshold_high = Column(Float, nullable=False)
    threshold_critically_high = Column(Float, nullable=False)
    sensor_unit = Column(String, nullable=False)
