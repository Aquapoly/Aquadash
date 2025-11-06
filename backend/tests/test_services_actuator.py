import datetime
import time
from app.services.actuator import get_actuator_activation
from app import models, schemas
from sqlalchemy.orm import Session
import pytest

@pytest.mark.parametrize("measurement", [None, models.Measurement()])
def test_get_actuator_activation_deactivated(dummy_actuators: list[models.Actuator], measurement):
    """Test the result of get_actuator_activation when actuator is deactivated"""
    actuator = dummy_actuators[0]
    actuator.enabled = False

    result = get_actuator_activation(actuator, measurement)
    assert result.activate == False


def test_get_actuator_activation_return_type(dummy_actuators: list[models.Actuator]):
    """Test the return type of get_actuator_activation"""
    actuator = dummy_actuators[0]
    last_measurement = models.Measurement(
        sensor_id=actuator.sensor_id,
        timestamp=datetime.datetime.now().astimezone(),
        value=5.0
    )

    result = get_actuator_activation(actuator, last_measurement)
    assert isinstance(result, schemas.ActuatorActivation), f"Result should be of type schemas.ActuatorActivation. was {type(result)}"
    assert isinstance(result.activate, bool), f"Activate should be a boolean. was {type(result.activate)}"
    assert isinstance(result.status, str), f"Status should be a string. was {type(result.status)}"
    assert isinstance(result.duration, float), f"Duration should be a float. was {type(result.duration)}"
    assert isinstance(result.period, float), f"Period should be a float. was {type(result.period)}"


def test_get_actuator_activation_missing_timestamp(dummy_actuators: list[models.Actuator]):
    """Test get_actuator_activation when last_measurement is missing timestamp"""
    actuator = dummy_actuators[0]
    last_measurement = models.Measurement(
        sensor_id=actuator.sensor_id,
        value=5.0
    )

    result = get_actuator_activation(actuator, last_measurement)
    assert isinstance(result, schemas.ActuatorActivation), f"Result should be of type schemas.ActuatorActivation, was {type(result)}"
    assert result.activate == False, "Actuator should not be activated when timestamp is missing"


def test_get_actuator_activation_missing_value(dummy_actuators: list[models.Actuator]):
    """Test get_actuator_activation when measurement has no value"""
    actuator = dummy_actuators[0]
    actuator.activation_period = 0.01
    time.sleep(0.02)
    last_measurement = models.Measurement(
        sensor_id=actuator.sensor_id,
        timestamp=datetime.datetime.now().astimezone()
    )

    result = get_actuator_activation(actuator, last_measurement)
    assert isinstance(result, schemas.ActuatorActivation), f"Result should be of type schemas.ActuatorActivation, was {type(result)}"
    assert result.activate == False, "Actuator should not be activated when value is missing"


def test_get_actuator_activation_old_timestamp(dummy_actuators: list[models.Actuator]):
    """Test get_actuator_activation when measurement has an old timestamp"""
    actuator = dummy_actuators[0]
    last_measurement = models.Measurement(
        sensor_id=actuator.sensor_id,
        timestamp=datetime.datetime(1999, 12, 31, 23, 59).astimezone(),
        value=5.0
    )

    result = get_actuator_activation(actuator, last_measurement)
    assert isinstance(result, schemas.ActuatorActivation), f"Result should be of type schemas.ActuatorActivation, was {type(result)}"
    assert result.activate == False, "Actuator should not be activated when timestamp is too old"


def test_get_actuator_activation_still_activated(dummy_actuators: list[models.Actuator]):
    """Test get_actuator_activation when actuator is already active"""
    actuator = dummy_actuators[0]
    actuator.activation_period = 1000
    last_measurement = models.Measurement(
        sensor_id=actuator.sensor_id,
        timestamp=datetime.datetime.now().astimezone(),
        value=5.0
    )

    result = get_actuator_activation(actuator, last_measurement)
    assert isinstance(result, schemas.ActuatorActivation), f"Result should be of type schemas.ActuatorActivation, was {type(result)}"
    assert result.activate == False, "Actuator should not be activated again when it is already active"


@pytest.mark.parametrize("actuator_modifications, measurement_value", [
    ([], 5.0),
    ([("activation_condition", models.ActivationCondition.low)], 0.5),
    ([("condition_value", -20.0)], -10.0),
    ([("condition_value", -100.0), ("activation_condition", models.ActivationCondition.low)], -105.0),
    ([("activation_condition", models.ActivationCondition.always)], 1.0),
    ([("activation_condition", models.ActivationCondition.always)], 2.0),
    ([("activation_condition", models.ActivationCondition.always)], -1.0),
    ([("activation_condition", models.ActivationCondition.low_or_high)], -1.0),
    ([("activation_condition", models.ActivationCondition.low_or_high)], 2.0)
])
def test_get_actuator_activation(dummy_actuators: list[models.Actuator], actuator_modifications, measurement_value):
    """Test result of get_actuator_activation when it should return active"""
    actuator = dummy_actuators[0]
    actuator.activation_period = 0.01
    time.sleep(0.02)

    for modification in actuator_modifications:
        actuator.__dict__[modification[0]] = modification[1]

    last_measurement = models.Measurement(
        sensor_id=actuator.sensor_id,
        timestamp=datetime.datetime.now().astimezone(),
        value=measurement_value
    )

    result = get_actuator_activation(actuator, last_measurement)
    assert isinstance(result, schemas.ActuatorActivation), f"Result should be of type schemas.ActuatorActivation, was {type(result)}"
    assert result.activate == True, "Actuator should be activated"


def test_get_actuator_activation_no_measurements(db_session: Session, dummy_actuators: list[schemas.Actuator]):
    """Test result of get_actuator_activation when there are no measurements"""
    result = get_actuator_activation(dummy_actuators[0], None)
    
    assert isinstance(result, schemas.ActuatorActivation), f"Result should be of type schemas.ActuatorActivation, was {type(result)}"
    assert result.activate == False, "Actuator should not be activated"