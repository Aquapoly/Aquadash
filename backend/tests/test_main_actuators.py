from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session
from app import models

def test_get_actuators(client: TestClient, db_session: Session, dummy_actuators: list[models.Actuator]):
    """Test /actuators/{prototype_id} endpoint to retrieve a prototype's actuators by its id"""
    prototype_id = db_session.get(models.Sensor, dummy_actuators[0].sensor_id).prototype_id

    response = client.get(f"/actuators/{prototype_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = response.json()
    data = [{key: val for key,val in i.items() if key not in ["enabled", "last_activated"]} for i in data]
    
    for actuator in dummy_actuators:
        assert {
            "actuator_type": actuator.actuator_type.name,
            "sensor_id": actuator.sensor_id,
            "condition_value": actuator.condition_value,
            "activation_condition": actuator.activation_condition.name,
            "activation_period": actuator.activation_period,
            "activation_duration": actuator.activation_duration,
            "actuator_id": actuator.actuator_id
        } in data, "Actuator should be in response"


def test_get_actuators_no_prototype(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /actuators/{prototype_id} endpoint with a non-existant prototype"""
    db_session.delete(dummy_prototype) # Ensure prototype doesn't exist

    response = client.get(f"/actuators/{dummy_prototype.prototype_id}")
    assert response.status_code == 404, f"Should return 404 for not found, got {response.status_code}"


def test_get_actuators_empty(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /actuators/{prototype_id} endpoint with no actuators"""
    actuators = db_session.query(models.Actuator).all()
    for actuator in actuators:
        db_session.delete(actuator)

    response = client.get(f"/actuators/{dummy_prototype.prototype_id}")
    assert response.status_code == 200, f"Should return 200 (prototype exists), got {response.status_code}"
    assert len(response.json()) == 0, f"Should return empty actuator list, got {len(response.json())} actuators"


def test_get_actuators_wrong_type(client: TestClient, dummy_actuators: list[models.Actuator]):
    """Test /actuators/{prototype_id} endpoint with wrong arguments"""
    response = client.get(f"/actuators/☻♥")
    assert response.status_code == 422, f"Should return 422 for unprocessable content, got {response.status_code}"


def test_post_actuator(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor], dummy_actuators: list[models.Actuator]):
    """Test /actuators endpoint to add an actuator"""
    new_actuator = {
        "actuator_type": models.ActuatorType.acid_pump.name,
        "sensor_id": dummy_sensors[0].sensor_id,
        "condition_value": 1.0,
        "activation_condition": models.ActivationCondition.high.name,
        "activation_period": 1.0,
        "activation_duration": 1.0
    }

    response = client.post("/actuators", json=new_actuator)
    assert response.status_code == 201, f"Should return 201 for ressource created, got {response.status_code}"
    assert db_session.get(models.Actuator, response.json()["actuator_id"]) is not None, "Should add actuator to database"


def test_post_actuator_missing_field(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    """Test /actuators endpoint to try to add an actuator with missing fields"""
    new_actuator = {
        "actuator_type": models.ActuatorType.acid_pump.name,
        "sensor_id": dummy_sensors[0].sensor_id,
        "condition_value": 1.0,
        "activation_condition": models.ActivationCondition.high.name,
    }

    response = client.post("/actuators", json=new_actuator)
    assert response.status_code == 400, f"Should return 400 for bad request, got {response.status_code}"


def test_post_actuator_duplicate_id(client: TestClient, db_session: Session, dummy_actuators: list[models.Actuator]):
    """Test /actuators endpoint to try to add an actuator with a duplicate id"""
    duplicate_actuator = {
        "actuator_id": dummy_actuators[0].actuator_id,
        "actuator_type": dummy_actuators[0].actuator_type.name,
        "sensor_id": dummy_actuators[0].sensor_id,
        "condition_value": dummy_actuators[0].condition_value,
        "activation_condition": dummy_actuators[0].activation_condition.name,
        "activation_period": dummy_actuators[0].activation_period,
        "activation_duration": dummy_actuators[0].activation_duration
    }

    response = client.post("/actuators", json=duplicate_actuator)
    assert response.status_code == 409, f"Should return 409 for duplicate id, got {response.status_code}"
    assert db_session.get(models.Actuator, dummy_actuators[0].actuator_id).activation_period != duplicate_actuator["activation_period"], \
        "Should not modify existing actuator"


def test_post_actuator_no_sensor(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    """Test /actuator endpoint to try to add an actuator to a non-existing sensor"""
    db_session.delete(dummy_sensors[0])

    new_actuator = {
        "actuator_type": models.ActuatorType.acid_pump.name,
        "sensor_id": dummy_sensors[0].sensor_id,
        "condition_value": 5.0,
        "activation_condition": models.ActivationCondition.high.name,
        "activation_period": 2.5,
        "activation_duration": 1.25
    }

    response = client.post("/actuators", json=new_actuator)
    assert response.status_code == 404, f"Should return not found, got {response.status_code}"
    assert db_session.query(models.Actuator).filter_by(sensor_id=dummy_sensors[0].sensor_id).count() == 0, \
        "Should not add actuator with non-existant sensor to DB"


@pytest.mark.parametrize("key, value", [("activation_period",-1.0),("activation_duration",-10.0)])
def test_post_actuator_impossible_value(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor], key, value):
    """Test /actuators endpoint to try to add an actuator with an impossible value"""
    new_actuator_template = {
        "actuator_type": models.ActuatorType.acid_pump.name,
        "sensor_id": dummy_sensors[0].sensor_id,
        "condition_value": 5.0,
        "activation_condition": models.ActivationCondition.high.name,
        "activation_period": 2.5,
        "activation_duration": 1.25
    }

    actuator = new_actuator_template.copy()
    actuator[key] = value
    
    response = client.post("/actuators", json=actuator)
    assert response.status_code == 400, f"Should return 400 for bad request, got {response.status_code}"
    for actuator in db_session.query(models.Actuator).all():
        assert actuator.__getattribute__(key) != value, "Should not add actuator with impossible values to DB"


def test_patch_actuator(client: TestClient, db_session: Session, dummy_actuators: list[models.Actuator]):
    """Test /actuators endpoint to modify an existing actuator"""
    modified_actuators = [{
        "actuator_id": actuator.actuator_id,
    } for actuator in dummy_actuators[0:6]]
    
    modified_actuators[0]["activation_period"] = 9999.0
    modified_actuators[1]["activation_duration"] = 8888.0
    modified_actuators[2]["condition_value"] = 7777.0
    modified_actuators[3]["actuator_type"] = models.ActuatorType.nutrients_A_pump
    modified_actuators[4]["activation_condition"] = models.ActivationCondition.low_or_high
    modified_actuators[5]["enabled"] = False

    response = client.patch("/actuators", json=modified_actuators)
    assert response.status_code == 200, f"Should return 200 for success, got {response.status_code}"
    # TODO assert les actuateurs ont ete modifies


def test_get_actuators_negative_id(client: TestClient, db_session: Session, dummy_actuators: list[models.Actuator]):
    """Test /actuators/{prototype_id} endpoint with a negative id"""
    response = client.get(f"/actuators/-1")
    assert response.status_code == 404, f"Should return 404 for bad request, got {response.status_code}"


def test_post_actuator_negative_id(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor]):
    """Test /actuators endpoint with a negative actuator id"""
    new_actuator = {
        "actuator_id": -1,
        "actuator_type": models.ActuatorType.base_pump.name,
        "sensor_id": dummy_sensors[0].sensor_id,
        "condition_value": 1.01,
        "activation_condition": models.ActivationCondition.low.name,
        "activation_period": 0.101,
        "activation_duration": 0.0101
    }

    response = client.post(f"/actuators", json=new_actuator)
    assert response.status_code == 404, f"Should return 404 for bad request, got {response.status_code}"
    assert db_session.get(models.Actuator, -1) is None, "Should not add actuator with negative id to DB"


def test_patch_actuator_negative_id(client: TestClient, db_session: Session, dummy_sensors: list[models.Sensor], dummy_actuators: list[models.Actuator]):
    """Test /actuators endpoint with a negative actuator id"""
    actuator = {"actuator_id": -1}

    response = client.post(f"/actuators", json=actuator)
    assert response.status_code == 404, f"Should return 404 for bad request, got {response.status_code}"