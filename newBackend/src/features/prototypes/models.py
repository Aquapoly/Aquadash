from sqlalchemy import (
    Column,
    String,
    Integer,
)

from ..database.database import Base

class Prototype(Base):
    __tablename__ = "prototypes"

    prototype_id = Column(Integer, primary_key=True)
    prototype_name = Column(String, nullable=False)