from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session

from datetime import datetime

from . import models, schemas


def create(db: Session, measurement:schemas.MeasurementBase):
    query = (
        insert(models.Measurement)
        .values(measurement.model_dump())
        .returning(models.Measurement)
    )
    return db.execute(query).scalars().first()

def get_last(db:Session, sensor_id:int):
    query = (
        select(models.Measurement)
        .where(models.Measurement.sensor_id == sensor_id)
        .order_by(models.Measurement.timestamp.desc())
    )
    return db.execute(query).scalars().first()

def get(db: Session,
    sensor_id: int,
    start_time: datetime | None = None,
    end_time: datetime | None = None,):
    request = select(models.Measurement).where(
            models.Measurement.sensor_id == sensor_id
    )
    if start_time:
        request = request.where(models.Measurement.timestamp > start_time)
    else:
        request = request.where(models.Measurement.timestamp < end_time)
    request = request.order_by(models.Measurement.timestamp)

    return db.execute(request).scalars().all()

def post(db:Session, measurement:models.Measurement):
    query = (
        insert(models.Measurement)
        .values(**measurement.model_dump())
        .returning(models.Measurement)
    )
    return db.execute(query).scalars().first()

def add(db:Session, measurement:models.Measurement):
    db.add(measurement)
    return measurement

def delete_all(db:Session):
    return db.query(models.Measurement).delete()

