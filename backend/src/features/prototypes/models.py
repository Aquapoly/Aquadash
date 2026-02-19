from sqlalchemy import (
    Column,
    String,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column

from ..database.database import Base

class Prototype(Base):
    __tablename__ = "prototypes"

    prototype_id:Mapped[int] = mapped_column(Integer, primary_key=True)
    prototype_name:Mapped[str] = mapped_column(String, nullable=False)