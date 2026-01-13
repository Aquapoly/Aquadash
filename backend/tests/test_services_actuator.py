import datetime
import time
from app.services.actuator import get_actuator_activation
from app import models, schemas
from sqlalchemy.orm import Session
import pytest

# Test get_actuator_activation
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
    ([], 5), # int instead of float
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


def test_get_actuator_activation_no_measurements(db_session: Session, dummy_actuators: list[models.Actuator]):
    """Test result of get_actuator_activation when there are no measurements"""
    result = get_actuator_activation(dummy_actuators[0], None)
    
    assert isinstance(result, schemas.ActuatorActivation), f"Result should be of type schemas.ActuatorActivation, was {type(result)}"
    assert result.activate == False, "Actuator should not be activated"


def test_get_actuator_activation_different_sensor(dummy_actuators: list[models.Actuator]):
    """Test result of get_actuator_activation when the measurement's sensor it different from the actuator's sensor"""
    actuator1 = dummy_actuators[0]
    actuator2 = dummy_actuators[-1]
    assert actuator1.sensor_id != actuator2.sensor_id, "Test error, actuators should not be from the same sensor"

    actuator1.activation_period = 0.01
    time.sleep(0.02)

    measurement = models.Measurement(
        sensor_id=actuator2.sensor_id,
        timestamp=datetime.datetime.now().astimezone(),
        value=5.0
    )

    result = get_actuator_activation(actuator1, measurement)
    assert isinstance(result, schemas.ActuatorActivation), f"Result should be of type schemas.ActuatorActivation, was {type(result)}"
    assert result.activate == False, "Actuator should not activate when the measurement does not come from the same sensor"


@pytest.mark.parametrize("value", ["1.0", "♥", False, True, {"value":2.0}, [1.0, 2.0], datetime.datetime.now().astimezone(), float("nan")])
def test_get_actuator_activation_invalid_value(dummy_actuators: list[models.Actuator], value):
    """Test result of get_actuator_activation with an invalid measurement value"""
    actuator = dummy_actuators[0]
    actuator.activation_period = 0.01
    time.sleep(0.02)

    measurement = models.Measurement(
        sensor_id=actuator.sensor_id,
        timestamp=datetime.datetime.now().astimezone(),
        value=value
    )

    result = get_actuator_activation(actuator, measurement)
    assert isinstance(result, schemas.ActuatorActivation), f"Result should be of type schemas.ActuatorActivation, was {type(result)}"
    assert result.activate == False, f"Actuator should not activate when the measurement has an invalid value of type {type(measurement.value)}"


def test_get_actuator_activation_negative_period(dummy_actuators: list[models.Actuator]):
    """Test result of get_actuator_activation with a negative activation period"""
    actuator = dummy_actuators[0]
    actuator.activation_period = -1.0

    measurement = models.Measurement(
        sensor_id=actuator.sensor_id,
        timestamp=datetime.datetime.now().astimezone(),
        value=5.0
    )

    result = get_actuator_activation(actuator, measurement)
    assert isinstance(result, schemas.ActuatorActivation), f"Result should be of type schemas.ActuatorActivation, was {type(result)}"
    assert result.activate == False, "Actuator should not activate when the activation period is negative"


def test_get_actuator_activation_zero_duration(dummy_actuators: list[models.Actuator]):
    """Test result of get_actuator_activation with a zero activation duration"""
    actuator = dummy_actuators[0]
    actuator.activation_period = 0.01
    actuator.activation_duration = 0
    time.sleep(0.02)

    measurement = models.Measurement(
        sensor_id=actuator.sensor_id,
        timestamp=datetime.datetime.now().astimezone(),
        value=5.0
    )

    result = get_actuator_activation(actuator, measurement)
    assert isinstance(result, schemas.ActuatorActivation), f"Result should be of type schemas.ActuatorActivation, was {type(result)}"
    assert result.activate == False, "Actuator should not activate when the activation duration is zero"