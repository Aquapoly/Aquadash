from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound

from . import manager, schemas, models


def create(db: Session, sensor: schemas.Sensor) -> models.Sensor:
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
    
    try:
        created = manager.create(db=db, sensor=sensor)
        db.commit()
        db.refresh(created)
        return created
    
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflict in database: {str(err)}",
        )
    

def get_all(db: Session):
    """
    Retrieve all sensors from database.
    Args:
        db (Session): SQLAlchemy session.
    Returns:
        list[models.Sensor]: List of all sensors.
    """
    return manager.get_all(db=db)
    
def get(db:Session, prototype_id:int):
    """
    Retrieves sensors from the database, optionally filtered by prototype ID.
    Args:
        db (Session): SQLAlchemy session.
        prototype_id (int): filters sensors by the given prototype ID.
    Returns:
        list[models.Sensor]: List of sensors matching the criteria.

    Raises:
        sqlalchemy.exc.SQLAlchemyError: If a database error occurs during the query.
    """
    
    sensors = manager.get_by_prototype(db=db, prototype_id=prototype_id)
    if(len(sensors) == 0) : 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No sensor found for Prototype Id {prototype_id}",
        )
    return sensors


def update(db: Session, sensor: schemas.Sensor):
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
    if not (
        sensor.threshold_critically_low
        <= sensor.threshold_low
        <= sensor.threshold_high
        <= sensor.threshold_critically_high
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Threshold values for sensor {sensor.sensor_id} are inconsistent",
        )

    try:
        updated_sensor = manager.update_sensor(db=db, sensor=sensor)
        if updated_sensor is None:
            raise NoResultFound
        db.commit()
        db.refresh(updated_sensor)
        return updated_sensor
    except NoResultFound:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor with id {sensor.sensor_id} not found",
        )
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflict in database: {err}",
        )


def update_multiple(db: Session, sensors: list[schemas.Sensor]):
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
        updated_sensors.append(update(db, sensor))
    return updated_sensors
