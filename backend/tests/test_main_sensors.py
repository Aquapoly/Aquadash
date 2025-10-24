from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import models

def test_get_sensors(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    """Test /sensors/{prototype_id} endpoint to retrieve a prototype's sensors by its id"""
    response = client.get(f"/sensors/{dummy_sensors[0].prototype_id}")
    assert response.status_code == 200, "Expected status code 200"
    data = response.json()
    
    for sensor in dummy_sensors:
        assert {
            "sensor_id": sensor.sensor_id,
            "sensor_type": sensor.sensor_type.name,
            "prototype_id": sensor.prototype_id,
            "threshold_critically_low": sensor.threshold_critically_low,
            "threshold_low": sensor.threshold_low,
            "threshold_high": sensor.threshold_high,
            "threshold_critically_high": sensor.threshold_critically_high,
            "sensor_unit": sensor.sensor_unit
        } in data, "Sensor should be in response"


def test_get_sensors_non_existent_prototype(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /sensors/{prototype_id} endpoint with a non-existent prototype id"""
    db_session.delete(dummy_prototype) # Remove the dummy prototype to ensure ID does not exist

    response = client.get(f"/sensors/{dummy_prototype.prototype_id}")
    assert response.status_code == 404, f"Expected status code 404 for not found prototype, got {response.status_code}"


def test_post_valid_sensor(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /sensors endpoint to add a valid sensor"""
    new_sensor = {
        "sensor_type": "temperature",
        "prototype_id": dummy_prototype.prototype_id,
        "sensor_unit": "units",
        "threshold_critically_low": 0,
        "threshold_low": 1,
        "threshold_high": 2,
        "threshold_critically_high": 3
    }

    response = client.post("/sensors/", json=new_sensor)
    assert response.status_code == 201, f"Expected status code 201 for created sensor, got {response.status_code}"

    sensor_in_db = db_session.get(models.Sensor, response.json()['sensor_id'])
    assert sensor_in_db is not None, "Sensor should be added to DB"


def test_post_invalid_type_sensor(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /sensors endpoint to add a sensor with invalid type"""
    invalid_sensor = {
        "sensor_type": "阿夸冲刺",
        "prototype_id": dummy_prototype.prototype_id,
        "sensor_unit": "units",
        "threshold_critically_low": 0,
        "threshold_low": 1,
        "threshold_high": 2,
        "threshold_critically_high": 3
    }

    response = client.post("/sensors/", json=invalid_sensor)
    assert response.status_code == 422, f"Expected status code 422 for unprocessable content, got {response.status_code}"

    sensors_in_db = db_session.query(models.Sensor).all()
    for sensor in sensors_in_db:
        assert sensor.sensor_type != "阿夸冲刺", "Should not add invalid sensor to DB"


def test_post_sensor_non_existent_prototype(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /sensors endpoint to add a sensor in a non-existent prototype"""
    db_session.delete(dummy_prototype) # Remove prototype to ensure ID does not exist

    new_sensor = {
        "sensor_type": "temperature",
        "prototype_id": dummy_prototype.prototype_id,
        "sensor_unit": "units",
        "threshold_critically_low": 0,
        "threshold_low": 1,
        "threshold_high": 2,
        "threshold_critically_high": 3
    }

    response = client.post("/sensors/", json=new_sensor)
    assert response.status_code == 404, f"Expected status code 404 for not found ressource, got {response.status_code}"

    sensors_in_db = db_session.query(models.Sensor).all()
    for sensor in sensors_in_db:
        assert sensor.prototype_id != dummy_prototype.prototype_id, "Should not add sensor for non-existent prototype"