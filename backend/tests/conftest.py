import pytest
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, get_db  # Import your existing setup
from random import randint
from app import models

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
    if transaction.is_active: # Some functions roll back transactions on error
        transaction.rollback()  # This reverts all changes made in the test
    connection.close()


@pytest.fixture
def client(db_session):
    # Override get_db to use our test session
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)


@pytest.fixture
def dummy_prototype(db_session: Session):
    """Insert dummy prototype in DB and return it"""
    random_id = randint(1, 9999)

    while random_id in db_session.query(models.Prototype.prototype_id).all():
        random_id = randint(1, 9999)

    new_proto = models.Prototype(prototype_id=random_id, prototype_name="Test Proto")
    db_session.add(new_proto)
    db_session.flush()
    yield new_proto


@pytest.fixture
def dummy_sensors(db_session: Session, dummy_prototype: models.Prototype):
    """Insert dummy sensors of all types in DB and return them"""
    new_sensors = []
    for sensor_type in models.SensorType:
        random_id = randint(1, 9999)
        while random_id in db_session.query(models.Sensor.sensor_id).all():
            random_id = randint(1, 9999)

        new_sensor = models.Sensor(
            sensor_id=random_id,
            sensor_type=sensor_type,
            prototype_id=dummy_prototype.prototype_id,
            threshold_critically_low=0,
            threshold_low=1,
            threshold_high=2,
            theshold_critically_high=3,
            sensor_unit="units"
        )
        db_session.add(new_sensor)
        new_sensors.append(new_sensor)
        
    db_session.flush()
    yield new_sensors