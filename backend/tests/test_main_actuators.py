import time
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app import models

# GET /actuators/{prototype_id}
def test_get_actuators(client: TestClient, db_session: Session, dummy_actuators: list[models.Actuator]):
    """Test /actuators/{prototype_id} endpoint to retrieve a prototype's actuators by its id"""
    prototype_id = db_session.get(models.Sensor, dummy_actuators[0].sensor_id).prototype_id

    response = client.get(f"/actuators/{prototype_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = response.json()
    data = [{key: val for key,val in i.items() if key not in ["enabled", "last_activated"]} for i in data] # Remove unwanted keys for comparison
    
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


def test_get_actuator_state_active(client: TestClient, db_session: Session, dummy_actuators: list[models.Actuator]):
    """Test /actuators/{actuator_id}/state endpoint to get the state of an active actuator"""
    # Make sure the measurement will not be in the activation period
    db_session.query(models.Actuator).filter_by(actuator_id=dummy_actuators[0].actuator_id).first().activation_period = 0.5
    time.sleep(1)
    db_session.add(models.Measurement(sensor_id=dummy_actuators[0].sensor_id, value=100))

    response = client.get(f"/actuators/{dummy_actuators[0].actuator_id}/state")
    assert response.status_code == 200, f"Should return 200, got {response.status_code}"
    assert response.json()["activate"] == True, "Actuator should be in active state"
    assert response.json()["duration"] == dummy_actuators[0].activation_duration, "Actuator should be active for the same duration"
    assert response.json()["period"] == dummy_actuators[0].activation_period, "Actuator should have the same period"


@pytest.mark.parametrize("condition, period, value", [
    (models.ActivationCondition.high,100,100),(models.ActivationCondition.high,0.5,0.5),
    (models.ActivationCondition.low,0.5,100), (models.ActivationCondition.low, 100, 0.5)])
def test_get_actuator_state_inactive(client: TestClient, db_session: Session, dummy_actuators: list[models.Actuator], condition, period, value):
    """Test /actuators/{actuator_id}/state endpoint to get the state of an inactive actuator"""
    # Make sure the measurement will be in the activation period
    db_session.query(models.Actuator).filter_by(actuator_id=dummy_actuators[0].actuator_id).first().activation_period = period
    db_session.query(models.Actuator).filter_by(actuator_id=dummy_actuators[0].actuator_id).first().activation_condition = condition
    db_session.add(models.Measurement(sensor_id=dummy_actuators[0].sensor_id, value=value))

    response = client.get(f"/actuators/{dummy_actuators[0].actuator_id}/state")
    assert response.status_code == 200, f"Should return 200, got {response.status_code}"
    assert response.json()["activate"] == False, "Actuator should be in inactive state"
    

def test_get_actuators_return_types(client: TestClient, db_session: Session, dummy_actuators: list[models.Actuator]):
    """Test /actuators/{prototype_id} endpoint to check if it returns the right types"""
    prototype_id = db_session.get(models.Sensor, dummy_actuators[0].sensor_id).prototype_id
    
    response = client.get(f"/actuators/{prototype_id}")
    actuator = response.json()[0]

    assert isinstance(actuator["sensor_id"], int), f"Sensor id should be an int, was {type(actuator['sensor_id'])}"
    assert isinstance(actuator["actuator_id"], int), f"Actuator id should be an int, was {type(actuator['actuator_id'])}"
    assert isinstance(actuator["actuator_type"], str), f"Actuator type should be a string, was {type(actuator['actuator_type'])}"
    assert isinstance(actuator["condition_value"], float), f"Condition value should be a float, was {type(actuator['condition_value'])}"
    assert isinstance(actuator["activation_condition"], str), f"Activation condition should be a string, was {type(actuator['activation_condition'])}"
    assert isinstance(actuator["activation_period"], float), f"Activation period should be a float, was {type(actuator['activation_period'])}"
    assert isinstance(actuator["activation_duration"], float), f"Activation duration should be a float, was {type(actuator['activation_duration'])}"
    assert isinstance(actuator["enabled"], bool), f"Enabled should be a boolean, was {type(actuator['enabled'])}"
    assert isinstance(actuator["last_activated"], str), f"Last activated should be a string, was {type(actuator['last_activated'])}"


def test_get_actuator_state_non_existent(client: TestClient, db_session: Session, dummy_actuators: list[models.Actuator]):
    """Test /actuators/{prototype_id}/state endpoint with a non existent actuator"""
    db_session.delete(dummy_actuators[0])

    response = client.get(f"/actuators/{dummy_actuators[0].actuator_id}/state")
    assert response.status_code == 404, f"Should return 404 for not found, got {response.status_code}"


# POST /actuators
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
    assert response.status_code == 404, f"Should return 404 for not found, got {response.status_code}"
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


# PATCH /actuators
@pytest.mark.parametrize("key, val", [
    ("activation_period", 9999.0), ("activation_duration", 8888.0), ("condition_value", 7777.0),
    ("actuator_type", models.ActuatorType.nutrients_A_pump.name), ("activation_condition", models.ActivationCondition.low_or_high.name),
    ("enabled", False)
])
def test_patch_actuator(client: TestClient, db_session: Session, dummy_actuators: list[models.Actuator], key, val):
    """Test /actuators endpoint to modify an existing actuator"""
    modified_actuator = {
        "actuator_id": dummy_actuators[0].actuator_id,
        key: val
    }

    response = client.patch("/actuators", json=[modified_actuator])
    assert response.status_code == 200, f"Should return 200 for success, got {response.status_code}"
    assert db_session.get(models.Actuator, dummy_actuators[0].actuator_id).__dict__[key] == val, "Should modify actuator"


def test_patch_actuator_not_existent(client: TestClient, db_session: Session, dummy_actuators: list[models.Actuator]):
    """Test /actuators endpoint with a non-existent actuator"""
    db_session.delete(dummy_actuators[0])
    actuator = {
        "actuator_id": dummy_actuators[0].actuator_id,
        "condition_value": 123
    }

    response = client.patch(f"/actuators", json=actuator)
    assert response.status_code == 404, f"Should return 404 for bad request, got {response.status_code}"
    assert db_session.get(models.Actuator, dummy_actuators[0].actuator_id).count() == 0, \
        "Should not add actuator to DB"


# PATCH /actuators/{actuator_id}/last_activated
def test_patch_actuator_last_activated(client: TestClient, db_session: Session, dummy_actuators: list[models.Actuator]):
    """Test /actuators/{actuator_id}/last_activated endpoint with a valid actuator"""
    
    response = client.patch(f"/actuators/{dummy_actuators[0].actuator_id}/last_activated")
    assert response.status_code == 200, f"Should return 200, got {response.status_code}"
    assert db_session.query(models.Actuator).order_by(desc(models.Actuator.last_activated)).first() == dummy_actuators[0], \
        "Should update given actuator's last_activated value"


def test_patch_actuator_last_activated_non_existent(client: TestClient, db_session: Session, dummy_actuators: list[models.Actuator]):
    """Test /actuators/{actuator_id}/last_activated endpoint with a non existent actuator"""
    db_session.delete(dummy_actuators[0])

    response = client.patch(f"/actuators/{dummy_actuators[0].actuator_id}/last_activated")
    assert response.status_code == 404, f"Should return 404 for not found, got {response.status_code}"


def test_patch_actuator_last_activated_invalid_actuator(client: TestClient, db_session: Session, dummy_actuators: list[models.Actuator]):
    """Test /actuators/{actuator_id}/last_activated endpoint with an invalid actuator"""

    response = client.patch(f"/actuators/ten/last_activated")
    assert response.status_code == 422, f"Should return 422 for unprocessable content, got {response.status_code}"