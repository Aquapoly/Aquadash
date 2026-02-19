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

from ..database.database import Base


# auth stuff
class User(Base):
    __tablename__ = "users"

    username:Mapped[str] = mapped_column(String, primary_key=True, nullable=False, unique=True)
    pw_salt:Mapped[str] = mapped_column(String, nullable=False)
    pw_hash:Mapped[str] = mapped_column(String, nullable=False)
    permissions:Mapped[int] = mapped_column(Integer, nullable=False)
    logged_in:Mapped[bool] = mapped_column(Boolean, nullable=False)