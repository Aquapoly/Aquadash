from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound

from . import repository, schemas, models

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
        created_sensor = repository.create(db=db, sensor=sensor)
        if created_sensor is None:
            raise IntegrityError
        db.commit()
        db.refresh(created_sensor)
        return created_sensor
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflict in database: {err}",
        )
    
    
def get_sensors(db:Session, prototype_id:int | None = None):
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
    
    if(prototype_id == None) : return repository.get_all(db=db)

    sensors = repository.get_by_prototype(db=db, prototype_id=prototype_id)
    if(len(sensors) == 0) : 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prototype Id {prototype_id} has no sensor",
        )
    return sensors


def update_sensor(db: Session, sensor: schemas.Sensor):
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
        updated_sensor = repository.update_sensor(db=db, sensor=sensor)
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


def update_sensors(db: Session, sensors: list[schemas.Sensor]):
    updated_sensors = []
    for sensor in sensors:
        updated_sensors.append(update_sensor(db, sensor))
    return updated_sensors