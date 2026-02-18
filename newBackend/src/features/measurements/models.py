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
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from ..database.database import Base


class Measurement(Base):
    __tablename__ = "measurements"

    measurement_id:Mapped[int] = mapped_column(Integer, primary_key=True)
    sensor_id:Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("sensors.sensor_id"), 
        nullable=False, 
        index=True
    )
    timestamp:Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now(), 
        index=True
    )
    value:Mapped[float] = mapped_column(Float, nullable=False)