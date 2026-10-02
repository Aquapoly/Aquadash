from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os

# SQLALCHEMY_DATABASE_URL = "sqlite:///./aquapoly.sqlite"
if os.environ.get("DOCKER") == "1":
    SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://postgres:aquapoly@db/aquapoly"
else:
    SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://postgres:aquapoly@localhost/aquapoly"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
