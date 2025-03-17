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

class Actuator(Base):
    __tablename__ = "actuators"
    actuator_id = Column(Integer, primary_key=True)
    actuator_type = Column(Enum(ActuatorType), nullable=False)
    sensor_id = Column(Integer, ForeignKey("sensors.sensor_id"), nullable=False)
    low = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    activation_condition = Column(Enum(ActivationCondition), nullable=False)
    activation_period = Column(Float, nullable=False)
    activation_duration = Column(Float, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    last_activated = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


# auth stuff
class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, nullable=False, unique=True)
    pw_salt = Column(String, nullable=False)
    pw_hash = Column(String, nullable=False)
    permissions = Column(Integer, nullable=False)
    logged_in = Column(Boolean, nullable=False)
