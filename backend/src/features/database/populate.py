
from sqlalchemy.orm import Session

from ..prototypes.service import get_by_id as get_prototypes, create as post_prototype
from ..prototypes.schemas import Prototype
from ..sensors.models import SensorType, Sensor
from ..sensors.service import get as get_sensors, create as post_sensor
from ..actuators.models import ActuatorType, Actuator
from ..actuators.service import get_by_prototype as get_actuators, create as post_actuator
from ..actuators.activation_condition import ActivationCondition



DEFAULT_PROTOTYPE_ID = 0

def default_populate(db: Session):
    """
    Populates the database with a default prototype, associated sensors, and an actuator if they do not already exist.
    Args:
        db (Session): SQLAlchemy session.
    Returns:
        dict: A dictionary containing the created or retrieved prototype, list of sensors, and actuator.
    Raises:
        HTTPException: If any database operation fails due to integrity errors or other issues.
    """
    # Check if the prototype already exists
    try:
        existing_prototype = get_prototypes(db=db, prototype_id=DEFAULT_PROTOTYPE_ID)
        if existing_prototype:
            prototype = existing_prototype[0]
    except:
        # Create a prototype
        prototype_data = Prototype(
            prototype_id=0,
            prototype_name="default_prototype"
        )
        prototype = post_prototype(db, prototype_data)

    # Create three sensors associated with the prototype
    sensors = []
    sensor_types = [
        (SensorType.ec, "mS/cm", 0.0, 1.0, 2.0, 3.0),
        (SensorType.ph, "pH", 0.0, 4.0, 7.0, 10.0),
        (SensorType.temperature, "Celsius", 0.0, 10.0, 30.0, 40.0)
    ]

    existing_sensors = get_sensors(db=db, prototype_id=DEFAULT_PROTOTYPE_ID)
     
    if not existing_sensors:
        for sensor_type, unit, crit_low, low, high, crit_high in sensor_types:   
            sensor_data = Sensor(
                sensor_type=sensor_type,
                prototype_id=DEFAULT_PROTOTYPE_ID,
                threshold_critically_low=crit_low,
                threshold_low=low,
                threshold_high=high,
                threshold_critically_high=crit_high,
                sensor_unit=unit
            )
            sensor = post_sensor(db, sensor_data)
            sensors.append(sensor)

    # Check if the actuator already exists
    existing_actuator = get_actuators(db=db, prototype_id=DEFAULT_PROTOTYPE_ID)
    if existing_actuator:
        actuator = existing_actuator[0]
    else:
        # Create one actuator associated with the first sensor
        actuator_data = Actuator(
            actuator_type=ActuatorType.acid_pump,  
            sensor_id=sensors[0].sensor_id,  
            condition_value=0.0,  
            activation_condition=ActivationCondition.low,  
            activation_period=5.0,  
            activation_duration=2.0,  
        )
        actuator = post_actuator(db, actuator_data)

    return {
        "prototype": prototype,
        "sensors": sensors,
        "actuator": actuator
    }