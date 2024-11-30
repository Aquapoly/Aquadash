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
from datetime import datetime


def get_prototypes(db: Session, prototype_id: int | None = None):
    query = select(models.Prototype)
    if prototype_id is not None:
        query = query.where(models.Prototype.prototype_id == prototype_id)
    return db.execute(query).scalars().all()


def post_prototype(db: Session, prototype: schemas.Prototype):
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
    query = select(models.Sensor)
    if prototype_id is not None:
        query = query.where(models.Sensor.prototype_id == prototype_id)
    return db.execute(query).scalars().all()


def post_sensor(db: Session, sensor: schemas.SensorBase):
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
    sensor_ids: list[int] = [
        sensor.sensor_id for sensor in get_sensors(db, prototype_id=prototype_id)
    ]
    request = select(models.Actuator).where(models.Actuator.sensor_id.in_(sensor_ids))
    return db.execute(request).scalars().all()


def get_actuator(db: Session, actuator_id: int):
    query = select(models.Actuator).where(models.Actuator.actuator_id == actuator_id)

    return db.execute(query).scalars().first()


def post_actuator(db: Session, actuator: schemas.ActuatorBase):
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
    end_time = datetime.now()
    start_time = end_time - time_delta
    return get_measurements(db=db, sensor_id=sensor_id, start_time=start_time)


def get_last_measurement(
    db: Session,
    sensor_id: int,
):
    query = (
        select(models.Measurement)
        .where(models.Measurement.sensor_id == sensor_id)
        .order_by(models.Measurement.timestamp.desc())
    )
    return db.execute(query).scalars().first()


def post_measurement(db: Session, measurement: schemas.MeasurementBase):
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
    updated_actuators = []
    for actuator in actuators:
        updated_actuators.append(update_actuator(db, actuator))
    return updated_actuators

def update_actuator_last_activated(db: Session, actuator_id: int):
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
    updated_sensors = []
    for sensor in sensors:
        updated_sensors.append(update_sensor(db, sensor))
    return updated_sensors

def default_populate_database(db: Session):
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
        (SensorType.temperature, "Celsius", 0.0, 10.0, 30.0, 40.0),
        (SensorType.ec, "mS/cm", 0.0, 1.0, 2.0, 3.0),
        (SensorType.ph, "pH", 0.0, 4.0, 7.0, 10.0)
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
            low=0.0,  
            high=1.0,
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
