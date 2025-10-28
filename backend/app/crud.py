from sqlalchemy import and_, insert, select, update
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.classes.activation_condition import ActivationCondition
from app.classes.actuator_type import ActuatorType
from .classes.sensor_type import SensorType

from . import models, schemas
import secrets
from .security import authentification
from .security import permissions
from datetime import datetime, timedelta
import random, pytz
from concurrent.futures import ThreadPoolExecutor


def get_prototypes(db: Session, prototype_id: int | None = None):
    """
    Retrieves prototypes from the database, optionally filtered by prototype ID.
    Args:
        db (Session): SQLAlchemy session.
        prototype_id (int | None, optional): If provided, filters results to the prototype with this ID.
    Returns:
        list[models.Prototype]: List of matching Prototype objects.
    """
    query = select(models.Prototype)
    if prototype_id is not None:
        query = query.where(models.Prototype.prototype_id == prototype_id)
    return db.execute(query).scalars().all()


def post_prototype(db: Session, prototype: schemas.Prototype):
    """
    Inserts a new prototype into the database.
    Args:
        db (Session): SQLAlchemy session.
        prototype (schemas.Prototype): Validated prototype data to add to the DB.
    Returns:
        models.Prototype: The created prototype.
    Raises:
        HTTPException: On integrity error (e.g., duplicate), raises 409 with details.
    """
    query = (
        insert(models.Prototype)
        .values(prototype.model_dump())
        .returning(models.Prototype)
    )
    try:
        result = db.execute(query).scalars().first()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Prototype with this id already exists",
        )

    db.commit()
    return result


def get_sensors(db: Session, prototype_id: int | None = None):
    """
    Retrieves sensors from the database, optionally filtered by prototype ID.
    Args:
        db (Session): SQLAlchemy session.
        prototype_id (int | None, optional): If provided, filters sensors by the given prototype ID.
    Returns:
        list[models.Sensor]: List of sensors matching the criteria.

    Raises:
        sqlalchemy.exc.SQLAlchemyError: If a database error occurs during the query.
    """
    query = select(models.Sensor)
    if prototype_id is not None:
        query = query.where(models.Sensor.prototype_id == prototype_id)
    return db.execute(query).scalars().all()


def post_sensor(db: Session, sensor: schemas.SensorBase):
    """
    Inserts a new sensor into the database.
    Args:
        db (Session): SQLAlchemy session used for database operations.
        sensor (schemas.SensorBase): Validated sensor data to be inserted.
    Returns:
        models.Sensor: The newly created sensor instance.
    Raises:
        HTTPException: If an integrity error occurs (e.g., duplicate entry), raises a 409 Conflict with error details.
    """
    query = insert(models.Sensor).returning(models.Sensor)
    try:
        result = db.execute(query, sensor.model_dump()).scalars().first()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflict in database: {err}",
        )

    db.commit()
    return result


def get_actuators(db: Session, prototype_id: int):
    """
    Retrieves all actuators associated with the sensors of a given prototype.
    Args:
        db (Session): SQLAlchemy session.
        prototype_id (int): The ID of the prototype whose actuators are to be fetched.
    Returns:
        list[models.Actuator]: List of actuators linked to the sensors of the specified prototype.
    """
    sensor_ids: list[int] = [
        sensor.sensor_id for sensor in get_sensors(db, prototype_id=prototype_id)
    ]
    request = select(models.Actuator).where(models.Actuator.sensor_id.in_(sensor_ids))
    return db.execute(request).scalars().all()


def get_actuator(db: Session, actuator_id: int):
    """
    Retrieves an actuator from the database by its ID.
    Args:
        db (Session): SQLAlchemy session.
        actuator_id (int): The unique identifier of the actuator to retrieve.
    Returns:
        models.Actuator | None: The actuator instance if found, otherwise None.
    """
    query = select(models.Actuator).where(models.Actuator.actuator_id == actuator_id)

    return db.execute(query).scalars().first()


def post_actuator(db: Session, actuator: schemas.ActuatorBase):
    """
    Inserts a new actuator into the database.
    Args:
        db (Session): SQLAlchemy session.
        actuator (schemas.ActuatorBase): Validated actuator data to add to the DB.
    Returns:
        models.Actuator: The created actuator.
    Raises:
        HTTPException: On integrity error (e.g., duplicate), raises 409 with details.
    """
    query = insert(models.Actuator).returning(models.Actuator)
    try:
        result = db.scalars(query, actuator.model_dump()).first()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error from db: {err}",
        )

    db.commit()
    return result


def get_measurements(
    db: Session,
    sensor_id: int,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
):
    """
    Retrieves measurements for a given sensor within an optional time range.
    Args:
        db (Session): SQLAlchemy session.
        sensor_id (int): ID of the sensor to retrieve measurements for.
        start_time (datetime, optional): Start of the time range (exclusive). Defaults to None.
        end_time (datetime, optional): End of the time range (exclusive). Defaults to None.
    Returns:
        list[models.Measurement]: List of measurements matching the criteria.
    """
    request = select(models.Measurement).where(
        models.Measurement.sensor_id == sensor_id
    )
    if start_time:
        request = request.where(models.Measurement.timestamp > start_time)
    if end_time:
        request = request.where(models.Measurement.timestamp < end_time)
    request = request.order_by(models.Measurement.timestamp)

    return db.execute(request).scalars().all()


def get_measurements_delta(
    db: Session,
    sensor_id: int,
    time_delta: datetime,
):
    """
    Retrieves measurements for a given sensor within a specified time delta.
    Args:
        db (Session): SQLAlchemy session.
        sensor_id (int): ID of the sensor to retrieve measurements for.
        time_delta (datetime): Time interval to look back from the current time.
    Returns:
        List[models.Measurement]: List of measurements within the specified time delta.
    Raises:
        None
    """
    end_time = datetime.now()
    start_time = end_time - time_delta
    return get_measurements(db=db, sensor_id=sensor_id, start_time=start_time)


def get_last_measurement(
    db: Session,
    sensor_id: int,
):
    """
    Retrieves the most recent measurement for a given sensor from the database.
    Args:
        db (Session): SQLAlchemy session.
        sensor_id (int): The ID of the sensor whose latest measurement is requested.
    Returns:
        models.Measurement | None: The latest measurement for the sensor, or None if not found.
    """
    query = (
        select(models.Measurement)
        .where(models.Measurement.sensor_id == sensor_id)
        .order_by(models.Measurement.timestamp.desc())
    )
    return db.execute(query).scalars().first()


def post_measurement(db: Session, measurement: schemas.MeasurementBase):
    """
    Inserts a new measurement into the database.
    Args:
        db (Session): SQLAlchemy session.
        measurement (schemas.MeasurementBase): Validated measurement data to add to the DB.
    Returns:
        models.Measurement: The created measurement.
    Raises:
        HTTPException: On integrity error (e.g., sensor does not exist), raises 422 with details.
    """
    query = (
        insert(models.Measurement)
        .values(**measurement.model_dump())
        .returning(models.Measurement)
    )
    try:
        result = db.execute(query).scalars().first()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Sensor with this id does not exist",
        )
    db.commit()
    return result


def post_user(db: Session, username: str, password: str):
    """
    Creates and inserts a new user into the database.
    Args:
        db (Session): SQLAlchemy session.
        username (str): Username for the new user.
        password (str): Plaintext password for the new user.
    Returns:
        models.User: The created user instance.
    Raises:
        IntegrityError: If a user with the same username already exists.
    """
    perm = permissions.Permissions()
    perm.modifify_sensors_and_prototype = True
    perm.get_measurment = True
    pw_salt = secrets.token_hex(nbytes=128)
    pw_hash = authentification.get_password_hash(password + pw_salt)
    db_new_user = models.User(
        username=username,
        pw_salt=pw_salt,
        pw_hash=pw_hash,
        permissions=perm.encode_to_int(),
        logged_in=True,
    )
    db.add(db_new_user)
    db.commit()
    db.refresh(db_new_user)
    return db_new_user

def update_actuator(db: Session, actuator: schemas.Actuator):
    """
    Updates an existing actuator in the database.
    Args:
        db (Session): SQLAlchemy session.
        actuator (schemas.Actuator): Validated actuator data to update in the DB.
    Returns:
        models.Actuator: The updated actuator.
    Raises:
        HTTPException: If an integrity error occurs (e.g., constraint violation), raises 422 with details.
        HTTPException: If the actuator_id does not exist, raises 400 with details.
    """
    query = (
        update(models.Actuator).
        where(models.Actuator.actuator_id == actuator.actuator_id).
        values(**actuator.model_dump()).
        returning(models.Actuator)
    )
    try:
        result = db.execute(query).scalars().first()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Integrity error in db: {err}",
        )
    db.commit()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Received an actuator with non existant actuator_id {actuator.actuator_id}",
        )
    return result

def update_actuators(db: Session, actuators: list[schemas.Actuator]):
    """
    Updates multiple actuators in the database.
    Args:
        db (Session): SQLAlchemy session.
        actuators (list[schemas.Actuator]): List of validated actuator data to update in the DB.
    Returns:
        list[models.Actuator]: List of updated actuator objects.
    Raises:
        HTTPException: If an actuator update fails, raises an appropriate HTTPException with details.
    """
    updated_actuators = []
    for actuator in actuators:
        updated_actuators.append(update_actuator(db, actuator))
    return updated_actuators

def update_actuator_last_activated(db: Session, actuator_id: int):
    """
    Updates the 'last_activated' timestamp of a specific actuator in the database.
    Args:
        db (Session): SQLAlchemy session.
        actuator_id (int): The unique identifier of the actuator to update.
    Returns:
        models.Actuator: The updated actuator instance.
    Raises:
        HTTPException: If an integrity error occurs during the update (422) or if the actuator_id does not exist (400).
    """
    query = (
        update(models.Actuator).
        where(models.Actuator.actuator_id == actuator_id).
        values(last_activated=datetime.now().astimezone()).
        returning(models.Actuator)
    )
    try:
        result = db.execute(query).scalars().first()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Integrity error in db: {err}",
        )
    db.commit()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Received an actuator with non existant actuator_id {actuator_id}",
        )
    return result

def update_sensor(db: Session, sensor: schemas.Sensor):
    """
    Updates an existing sensor in the database.
    Args:
        db (Session): SQLAlchemy session.
        sensor (schemas.Sensor): Validated sensor data to update in the DB.
    Returns:
        models.Sensor: The updated sensor object.
    Raises:
        HTTPException: If an integrity error occurs (e.g., constraint violation), raises 422 with details.
        HTTPException: If the sensor_id does not exist, raises 400 with details.
    """
    query = (
        update(models.Sensor).
        where(models.Sensor.sensor_id == sensor.sensor_id).
        values(**sensor.model_dump()).
        returning(models.Sensor)
    )
    try:
        result = db.execute(query).scalars().first()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Integrity error in db: {err}",
        )
    db.commit()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Received a sensor with non existant sensor_id {sensor.sensor_id}",
        )
    return result

def update_sensors(db: Session, sensors: list[schemas.Sensor]):
    """
    Updates multiple sensors in the database.
    Args:
        db (Session): SQLAlchemy session.
        sensors (list[schemas.Sensor]): List of validated sensor data to update in the DB.
    Returns:
        list[models.Sensor]: List of updated sensor objects.
    Raises:
        HTTPException: If an update fails (e.g., sensor not found), raises appropriate HTTP error.
    """
    updated_sensors = []
    for sensor in sensors:
        updated_sensors.append(update_sensor(db, sensor))
    return updated_sensors

def default_populate_database(db: Session):
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
    existing_prototype = get_prototypes(db=db, prototype_id=0)
    if existing_prototype:
        prototype = existing_prototype[0]
    else:
        # Create a prototype
        prototype_data = schemas.Prototype(
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

    existing_sensors = get_sensors(db=db, prototype_id=prototype.prototype_id)
     
    if not existing_sensors:
        for sensor_type, unit, crit_low, low, high, crit_high in sensor_types:   
            sensor_data = schemas.SensorBase(
                sensor_type=sensor_type,
                prototype_id=prototype.prototype_id,
                threshold_critically_low=crit_low,
                threshold_low=low,
                threshold_high=high,
                threshold_critically_high=crit_high,
                sensor_unit=unit
            )
            sensor = post_sensor(db, sensor_data)
            sensors.append(sensor)

    # Check if the actuator already exists
    existing_actuator = get_actuators(db=db, prototype_id=prototype.prototype_id)
    if existing_actuator:
        actuator = existing_actuator[0]
    else:
        # Create one actuator associated with the first sensor
        actuator_data = schemas.ActuatorBase(
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

def generate_smooth_values(middle:float,rnge:float, nb_meas:int, alpha:float, threshold:float, drift_adjustment:float):
    """
    Generates a list of smoothed random values based on a Gaussian distribution and smoothing parameters.
    Args:
        middle (float): The mean value around which to generate measurements.
        rnge (float): The standard deviation for the Gaussian distribution.
        nb_meas (int): The number of measurements to generate.
        alpha (float): Smoothing factor (between 0 and 1) for exponential smoothing.
        threshold (float): Maximum allowed change between consecutive smoothed values.
        drift_adjustment (float): Factor to adjust drift towards the mean.
    Returns:
        list[float]: List of smoothed and threshold-limited random values.
    """
    values = []
    drift_adjustment = 0.20
    values.append(round(random.gauss(middle,rnge), 2))
    for i in range(1, nb_meas):
        new_val = round(random.gauss(middle,rnge),2) + drift_adjustment*(middle-values[i-1])*0.5
        smooth_value = alpha*new_val + (1-alpha)*values[i-1]
        if abs(smooth_value - values[i-1]) > threshold:
            smooth_value = values[i-1] - threshold if smooth_value < values[i-1] else values[i-1] + threshold
        values.append(round(smooth_value,2))
    return values

def generate_timestamps(nb_meas:int, rnge:str):
    """
    Generates a sorted list of random timestamps within a specified time range.
    Args:
        nb_meas (int): Number of timestamps to generate.
        rnge (str): Time range for the timestamps. Accepted values are "year", "day", or "hour".
    Returns:
        list: Sorted list of string representations of randomly generated timestamps within the specified range.
    Raises:
        ValueError: If the provided range is not one of "year", "day", or "hour".
    """
    timestamps = []
    for i in range(nb_meas):
        now = datetime.now(pytz.UTC)
        if   rnge == "year": startingDate = now - timedelta(days=365)
        elif rnge == "day": startingDate = now - timedelta(days=1)
        elif rnge == "hour" : startingDate = now - timedelta(hours=1)
        delta     = now-startingDate
        timestamp =  startingDate + timedelta(seconds=random.randint(0, int(delta.total_seconds())))
        timestamps.append(f"'{timestamp}'")
    sorted_copy = sorted(timestamps.copy())
    return sorted_copy

def generate_meas(nb_meas: int, year_ratio: float, day_ratio: float, hour_ratio: float, deviation_percent: float, smoothing_factor: float, drift_adjustment: float, db: Session):
    """
    Generates synthetic measurement data for all sensors in the database, distributing measurements across yearly, daily, and hourly intervals.
    Args:
        nb_meas (int): Total number of measurements to generate (will be adjusted to be divisible by the number of sensors).
        year_ratio (float): Proportion of measurements to assign to the yearly interval.
        day_ratio (float): Proportion of measurements to assign to the daily interval.
        hour_ratio (float): Proportion of measurements to assign to the hourly interval.
        deviation_percent (float): Percentage of deviation to apply to the generated values.
        smoothing_factor (float): Factor controlling the smoothness of the generated values.
        drift_adjustment (float): Adjustment factor for value drift over time.
        db (Session): SQLAlchemy session for database access.
    Returns:
        list: A list of lists, each containing [sensor_id, value, timestamp] for each generated measurement.
    Raises:
        ValueError: If the number of sensors in the database is zero.
    """
    request = db.query(models.Sensor).all()
    nb_sensors = len(request)
    while nb_meas % nb_sensors != 0: nb_meas += 1

    nb_year_meas = int(nb_meas * year_ratio)
    nb_day_meas = int(nb_meas * day_ratio)
    nb_hour_meas = int(nb_meas * hour_ratio)
    nb_meas_per_sensor = (nb_year_meas + nb_day_meas + nb_hour_meas) // nb_sensors

    def generate_sensor_values(sensor):
        """
        Generates simulated sensor values based on sensor thresholds and configuration parameters.
        Args:
            sensor: An object representing the sensor, expected to have 'threshold_critically_high', 'threshold_critically_low', and 'sensor_id' attributes.
        Returns:
            tuple: A tuple containing the sensor ID and a list of generated smooth values.
        Raises:
            AttributeError: If the sensor object does not have the required attributes.
        """
        value_range = ((sensor.threshold_critically_high - sensor.threshold_critically_low) * deviation_percent / 2)
        middle = (sensor.threshold_critically_high + sensor.threshold_critically_low) / 2
        threshold = value_range / 2
        return sensor.sensor_id, generate_smooth_values(middle, value_range, nb_meas_per_sensor, smoothing_factor, threshold, drift_adjustment)

    with ThreadPoolExecutor() as executor:
        values = dict(executor.map(generate_sensor_values, request))

    timestamps = {
        "year": generate_timestamps(nb_year_meas, "year"),
        "day": generate_timestamps(nb_day_meas, "day"),
        "hour": generate_timestamps(nb_hour_meas, "hour")
    }

    def distribute_meas(nb, time_key):
        """
        Distributes measurement values and timestamps across sensors.
        Args:
            nb (int): Number of measurements to distribute.
            time_key (str): Key to access the relevant timestamps.
        Returns:
            list: A list of lists, each containing [sensor_id, value, timestamp] for each measurement.
        Raises:
            KeyError: If a sensor_id or time_key does not exist in the corresponding dictionary.
            IndexError: If the indices exceed the available values or timestamps.
        """
        index, sensor_index = 0, 0
        result = []
        for i in range(nb):
            result.append([sensor_ids[sensor_index], values[sensor_ids[sensor_index]][index], timestamps[time_key][i]])
            sensor_index += 1
            if sensor_index == nb_sensors:
                index += 1
                sensor_index = 0
        return result

    sensor_ids = list(values.keys())
    return distribute_meas(nb_year_meas, "year") + distribute_meas(nb_day_meas, "day") + distribute_meas(nb_hour_meas, "hour")
