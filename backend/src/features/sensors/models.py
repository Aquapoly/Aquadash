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
from sqlalchemy.orm import Mapped, mapped_column

import enum

from ..database.database import Base

class SensorType(enum.Enum):
    temperature = "temperature"
    humidity = "humidity"
    ec = "ec"
    ph = "ph"
    water_level = "water_level"
    boolean_water_level = "boolean_water_level"
    oxygen = "oxygen"

class Sensor(Base):
    __tablename__ = "sensors"

    sensor_id:Mapped[int] = mapped_column(Integer, primary_key=True)
    sensor_type = Column(Enum(SensorType), nullable=False)
    prototype_id:Mapped[int] = mapped_column(
        Integer, ForeignKey("prototypes.prototype_id"), nullable=False
    )
    threshold_critically_low:Mapped[float] = mapped_column(Float, nullable=False)
    threshold_low:Mapped[float] = mapped_column(Float, nullable=False)
    threshold_high:Mapped[float] = mapped_column(Float, nullable=False)
    threshold_critically_high:Mapped[float] = mapped_column(Float, nullable=False)
    sensor_unit:Mapped[str] = mapped_column(String, nullable=False)

