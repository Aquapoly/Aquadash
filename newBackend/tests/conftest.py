import pytest
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from src.main import app
from src.features.database.database import Base, engine, get_db  # Import your existing setup

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session

    session.close()
    transaction.rollback()  # This reverts all changes made in the test
    connection.close()

@pytest.fixture
def client(db_session):
    # Override get_db to use our test session
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)