from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os

dbhost = "db" if os.environ.get("DOCKER") == "1" else "localhost"
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://postgres:aquapoly@{dbhost}/aquapoly"

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
