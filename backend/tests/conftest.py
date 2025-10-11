import pytest
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, get_db  # Import your existing setup

# TODO Find best scope for fixtures
@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    session.begin_nested() # DB savepoint
    yield session

    session.close()
    transaction.rollback()  # This reverts all changes made in the test
    connection.close()

@pytest.fixture
def client(db_session):
    # Override get_db to use our test session
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)