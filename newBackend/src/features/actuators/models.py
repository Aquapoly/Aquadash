from sqlalchemy import (
    Enum,
    Column,
    Integer,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

import enum
from .activation_condition import ActivationCondition

from ..database.database import Base


class ActuatorType(enum.Enum):
    acid_pump = "acid_pump"
    base_pump = "base_pump"
    nutrients_A_pump = "nutrients_A_pump"
    nutrients_B_pump = "nutrients_B_pump"

class Actuator(Base):
    __tablename__ = "actuators"
    actuator_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actuator_type = Column(Enum(ActuatorType), nullable=False)
    sensor_id: Mapped[int] = mapped_column(Integer, ForeignKey("sensors.sensor_id"), nullable=False)
    condition_value: Mapped[float] = mapped_column(Float, nullable=False)
    activation_condition = Column(Enum(ActivationCondition), nullable=False)
    activation_period: Mapped[float] = mapped_column(Float, nullable=False)
    activation_duration: Mapped[float] = mapped_column(Float, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_activated: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
