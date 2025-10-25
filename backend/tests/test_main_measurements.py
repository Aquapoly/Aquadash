from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import models

def test_get_last_measurement(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    pass


def test_get_last_measurement_no_sensor(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    pass


def test_get_last_measurement_no_measurements(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    pass


def test_get_measurements_sensor(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    pass


def test_get_measurements_no_sensor(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    pass


def test_get_measurements_no_measurements(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    pass


def test_get_measurements_time_range(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    pass


def test_post_measurement(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    pass


def test_post_measurement_no_sensor(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    pass


def test_post_measurement_invalid_value(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    pass


def test_post_measurement_missing_data(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    pass