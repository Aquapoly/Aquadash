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

    response = client.post("/sensors", json=new_sensor)
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

    response = client.post("/sensors", json=invalid_sensor)
    assert response.status_code == 422, f"Expected status code 422 for unprocessable content, got {response.status_code}"

    sensors_in_db = db_session.query(models.Sensor).all()
    for sensor in sensors_in_db:
        assert sensor.sensor_type.name != "阿夸冲刺", "Should not add invalid sensor to DB"


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

    response = client.post("/sensors", json=new_sensor)
    assert response.status_code == 404, f"Expected status code 404 for not found ressource, got {response.status_code}"

    sensors_in_db = db_session.query(models.Sensor).all()
    for sensor in sensors_in_db:
        assert sensor.prototype_id != dummy_prototype.prototype_id, "Should not add sensor for non-existent prototype"


def test_post_invalid_sensor_thresholds(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /sensors endpoint to add a sensor with invalid thresholds"""
    invalid_sensor_1 = {
        "sensor_type": "temperature",
        "prototype_id": dummy_prototype.prototype_id,
        "sensor_unit": "units",
        "threshold_critically_low": 5.0, # Low is higher than high
        "threshold_low": 4.0,
        "threshold_high": 3.0,
        "threshold_critically_high": 2.0
    }

    response = client.post("/sensors", json=invalid_sensor_1)
    assert response.status_code == 422, f"Expected status code 422 for unprocessable content, got {response.status_code}"

    sensors_in_db = db_session.query(models.Sensor).all()
    for sensor in sensors_in_db:
        assert { # Ignore sensor_id
            "sensor_type": sensor.sensor_type.name,
            "prototype_id": sensor.prototype_id,
            "sensor_unit": sensor.sensor_unit,
            "threshold_critically_low": sensor.threshold_critically_low,
            "threshold_low": sensor.threshold_low,
            "threshold_high": sensor.threshold_high,
            "threshold_critically_high": sensor.threshold_critically_high
        } != invalid_sensor_1, "Should not add sensor with invalid thresholds to DB"


def test_patch_sensor(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    """Test /sensors/{sensor_id} endpoint to update a sensor"""
    updated_sensors = [
        {
            "sensor_type": sensor.sensor_type.name,
            "prototype_id": sensor.prototype_id,
            "sensor_unit": "measurements",
            "threshold_critically_low": sensor.threshold_critically_low + 1,
            "threshold_low": sensor.threshold_low + 1,
            "threshold_high": sensor.threshold_high + 1,
            "threshold_critically_high": sensor.threshold_critically_high + 1,
            "sensor_id": sensor.sensor_id
        } for sensor in dummy_sensors
    ]

    response = client.patch(f"/sensors", json=updated_sensors)
    assert response.status_code == 200, f"Expected status code 200 for OK, got {response.status_code}"

    for sensor in updated_sensors:
        s = db_session.get(models.Sensor, sensor['sensor_id'])
        assert s is not None, "Shold not delete sensor from DB"
        assert sensor["sensor_type"] == s.sensor_type.name, "Should update sensor type"
        assert sensor["prototype_id"] == s.prototype_id, "Should not update prototype id"
        assert sensor["sensor_unit"] == s.sensor_unit, "Should update sensor unit"
        assert sensor["threshold_critically_low"] == s.threshold_critically_low, "Should update sensor critically low threshold"
        assert sensor["threshold_low"] == s.threshold_low, "Should update sensor low threshold"
        assert sensor["threshold_high"] == s.threshold_high, "Should update sensor high threshold"
        assert sensor["threshold_critically_high"] == s.threshold_critically_high, "Should update sensor critically high threshold"


def test_patch_non_existent_sensor(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    """Test /sensors endpoint to update a non-existent sensor"""
    db_session.delete(dummy_sensors[0]) # Ensure ID does not exist

    sensor = {
        "sensor_type": dummy_sensors[0].sensor_type.name,
        "prototype_id": dummy_sensors[0].prototype_id,
        "sensor_unit": dummy_sensors[0].sensor_unit,
        "threshold_critically_low": dummy_sensors[0].threshold_critically_low,
        "threshold_low": dummy_sensors[0].threshold_low,
        "threshold_high": dummy_sensors[0].threshold_high,
        "threshold_critically_high": dummy_sensors[0].threshold_critically_high,
        "sensor_id": dummy_sensors[0].sensor_id
    }

    response = client.patch(f"/sensors", json=[sensor])
    assert response.status_code == 404, f"Expected status code 404 for not found, got {response.status_code}"
    assert db_session.get(models.Sensor, sensor['sensor_id']) is None, "Should not add DB"

    
def test_get_sensors_return_types(client: TestClient, db_session: Session,  dummy_sensors: list[models.Sensor]):
    """Test /sensors/{prototype_id} endpoint to check if it returns the right types"""

    response = client.get(f"/sensors/{dummy_sensors[0].prototype_id}")
    data = response.json()[0]

    assert isinstance(data["sensor_id"], int), f"Sensor id should be an int, was {type(data['sensor_id'])}"
    assert isinstance(data["prototype_id"], int), f"Prototype id should be an int, was {type(data['prototype_id'])}"
    assert isinstance(data["sensor_type"], str), f"Senor type should be a string, was {type(data['sensor_type'])}"
    assert isinstance(data["sensor_unit"], str), f"Senor unit should be a string, was {type(data['sensor_unit'])}"
    assert isinstance(data["threshold_critically_low"], float), f"Crit low thresh should be a float, was {type(data['threshold_critically_low'])}"
    assert isinstance(data["threshold_low"], float), f"Low thresh should be a float, was {type(data['threshold_low'])}"
    assert isinstance(data["threshold_high"], float), f"High thresh should be a float, was {type(data['threshold_high'])}"
    assert isinstance(data["threshold_critically_high"], float), f"Crit high thresh should be a float, was {type(data['threshold_critically_high'])}"