from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session

from . import models, schemas


def create(db: Session, sensor: schemas.Sensor) -> models.Sensor:
    """
    Inserts a new sensor into the database.

    Args:
        db (Session): SQLAlchemy session.
        sensor (schemas.Sensor): Sensor data to add.

    Returns:
        models.Sensor | None: The created sensor object, or None if creation fails.
    """
    query = (
        insert(models.Sensor)
        .values(**sensor.model_dump())
        .returning(models.Sensor)
    )
    result = db.execute(query).scalars().first()
    if result is None:
        raise ValueError("Failed to create sensor")
    return result


def get_all(db: Session):
    """Return all sensors."""
    query = select(models.Sensor)
    return db.execute(query).scalars().all()


def get_by_prototype(db: Session, prototype_id: int):
    """Return sensors filtered by prototype_id."""
    query = (
        select(models.Sensor)
        .where(models.Sensor.prototype_id == prototype_id)
    )
    return db.execute(query).scalars().all()


def update_sensor(db: Session, sensor: schemas.Sensor):
    query = (
        update(models.Sensor)
        .where(models.Sensor.sensor_id == sensor.sensor_id)
        .values(**sensor.model_dump())
        .returning(models.Sensor)
    )
    return db.execute(query).scalars().first()