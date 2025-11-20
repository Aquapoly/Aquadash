from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session
from app import models

def test_get_last_measurement(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    """Test /measurements/{sensor_id}/last endpoint"""
    db_session.add(models.Measurement(
        sensor_id=dummy_sensors[0].sensor_id,
        timestamp='2000-01-01T01:01:00.100000Z',
        value=5.0)
    )
    
    db_session.add(models.Measurement(
        sensor_id=dummy_sensors[0].sensor_id,
        value=50000.0)
    )

    response = client.get(f"/measurements/{dummy_sensors[0].sensor_id}/last")
    assert response.status_code == 200, "Should return 200 OK"
    data = response.json()
    assert data["sensor_id"] == dummy_sensors[0].sensor_id, "Sensor ID should match"
    assert data["value"] == 50000.0, "Measurement value should match"
    assert data["timestamp"] != None, "Timestamp should exist"


def test_get_last_measurement_no_sensor(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    """Test /measurements/{sensor_id}/last endpoint with non-existing sensor"""
    db_session.delete(dummy_sensors[0]) # Ensure sensor does not exist

    response = client.get(f"/measurements/{dummy_sensors[0].sensor_id}/last")
    assert response.status_code == 404, f"Should return 404 for not found, got {response.status_code}"


def test_get_last_measurement_no_measurements(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    """Test /measurements/{sensor_id}/last endpoint with no measurements"""
    measurements = db_session.query(models.Measurement).filter(models.Measurement.sensor_id == dummy_sensors[0].sensor_id).all()
    for measurement in measurements:    
        db_session.delete(measurement)  # Ensure no measurements exist

    response = client.get(f"/measurements/{dummy_sensors[0].sensor_id}/last")
    assert response.status_code == 404, f"Should return 404 for not found, got {response.status_code}"


def test_get_measurements_sensor(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor], dummy_measurements: list[models.Measurement]):
    """Test /measurements/{sensor_id} endpoint"""
    for sensor in dummy_sensors:
        response = client.get(f"/measurements/{sensor.sensor_id}")
        assert response.status_code == 200, f"Should return 200 OK, got {response.status_code}"
        assert len(response.json()) == 1, "Should respond with one measurement"


def test_get_measurements_no_sensor(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    """Test /measurements/{sensor_id} endpoint with non-existing sensor"""
    db_session.delete(dummy_sensors[0]) # Ensure sensor does not exist

    response = client.get(f"/measurements/{dummy_sensors[0].sensor_id}")
    assert response.status_code == 404, f"Should return 404 for not found, got {response.status_code}"


def test_get_measurements_no_measurements(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor], dummy_measurements: list[models.Measurement]):
    """Test /measurements/{sensor_id} endpoint with no measurements"""
    measurements = db_session.query(models.Measurement).filter(models.Measurement.sensor_id == dummy_sensors[0].sensor_id).all()
    for measurement in measurements:    
        db_session.delete(measurement)  # Ensure no measurements exist

    response = client.get(f"/measurements/{dummy_sensors[0].sensor_id}")
    assert response.status_code == 200, f"Should return 200 OK, got {response.status_code}"
    assert len(response.json()) == 0, "Should respond with zero measurements"


def test_get_measurements_time_range(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor], dummy_measurements: list[models.Measurement]):
    """Test /measurements/{sensor_id} endpoint with time range"""
    db_session.query(models.Measurement).delete()

    db_session.add(models.Measurement(
        sensor_id=dummy_sensors[0].sensor_id,
        timestamp='2000-01-01T01:01:00.100000Z', # Too early
        value=10.0
    ))
    db_session.add(models.Measurement(
        sensor_id=dummy_sensors[0].sensor_id,
        timestamp='2002-01-01T01:01:00.100000Z', # Within range
        value=20.0
    ))
    db_session.add(models.Measurement(
        sensor_id=dummy_sensors[0].sensor_id,
        timestamp='2004-01-01T01:01:00.100000Z', # Too late
        value=30.0
    ))

    response = client.get(f"/measurements/{dummy_sensors[0].sensor_id}", 
                          params={"start_time": "2001-01-01T01:01:00.100000Z", "end_time": "2003-01-01T01:01:00.100000Z"}
    )
    assert response.status_code == 200, f"Should return 200 OK, got {response.status_code}"
    assert len(response.json()) == 1, "Should respond with one measurement in time range"


def test_post_measurement(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    """Test /measurements endpoint to add a measurement"""
    measurement = {
        "sensor_id": dummy_sensors[0].sensor_id,
        "value": 707.0
    }

    response = client.post("/measurements", json=measurement)
    assert response.status_code == 201, f"Should return 201 for ressource created, got {response.status_code}"
    assert response.json()["sensor_id"] == dummy_sensors[0].sensor_id, "Sensor ID should match"
    assert response.json()["value"] == 707.0, "Measurement value should match"


def test_post_measurement_no_sensor(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    """Test /measurements endpoint to add a measurement for non-existing sensor"""
    db_session.delete(dummy_sensors[0]) # Ensure sensor does not exist

    measurement = {
        "sensor_id": dummy_sensors[0].sensor_id,
        "value": 707.0
    }

    response = client.post("/measurements", json=measurement)
    assert response.status_code == 404, f"Should return 404 for not found sensor, got {response.status_code}"


def test_post_measurement_invalid_value(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    """Test /measurements endpoint to add a measurement with invalid value"""
    measurement = {
        "sensor_id": dummy_sensors[0].sensor_id,
        "value": "invalid_value"
    }

    response = client.post("/measurements", json=measurement)
    assert response.status_code == 422, f"Should return 422 for unprocessable entity, got {response.status_code}"


def test_post_measurement_missing_data(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    """Test /measurements endpoint to add a measurement with missing data"""
    measurements = [
        {"sensor_id": dummy_sensors[0].sensor_id},
        {"value": 123.0},
        { }
    ]
    
    for measurement in measurements:
        response = client.post("/measurements", json=measurement)
        assert response.status_code == 422, f"Should return 422 for unprocessable entity, got {response.status_code}"


def test_get_measurements_return_types(client: TestClient, db_session: Session, dummy_measurements: list[models.Measurement]):
    """Test /measurements/{sensor_id} endpoint to check return types are correct"""
    response = client.get(f"/measurements/{dummy_measurements[0].sensor_id}")
    measurement = response.json()[0]

    assert isinstance(measurement["value"], float), f"Value should be a float, got {type(measurement['value'])}"
    assert isinstance(measurement["timestamp"], str), f"Timestamp should be a string, got {type(measurement['timestamp'])}"
    assert isinstance(measurement["sensor_id"], int), f"Sensor id should be an int, got {type(measurement['sensor_id'])}"
    assert isinstance(measurement["measurement_id"], int), f"Measurement id should be an int, got {type(measurement['measurement_id'])}"


@pytest.mark.parametrize("num_measurements", [1, 5, 10, 100, 1000])
def test_get_measurements_multiple(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor], num_measurements):
    """Test /measurements/{sensor_id} endpoint to check if it returns all the measurements"""
    db_session.query(models.Measurement).filter_by(sensor_id=dummy_sensors[0].sensor_id).delete() # Start with 0

    for _ in range(num_measurements):
        db_session.add(models.Measurement(
            sensor_id=dummy_sensors[0].sensor_id,
            timestamp="2000-01-01T01:01:00.100000Z",
            value=5.0
        )
    )
    
    response = client.get(f"/measurements/{dummy_sensors[0].sensor_id}")
    assert response.status_code == 200, "Expected status code 200"
    assert len(response.json()) == num_measurements, f"Expected {num_measurements} measurements but got {len(response.json())}"