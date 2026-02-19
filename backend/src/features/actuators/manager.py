from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session


from . import models, schemas
from datetime import datetime


def get(db:Session, id:int):
    query = select(models.Actuator).where(models.Actuator.actuator_id == id)
    return db.execute(query).scalars().first()

def get_by_prototype(db: Session, sensor_ids: list[int]):

    query = (
        select(models.Actuator)
        .where(models.Actuator.sensor_id.in_(sensor_ids))
    )
    return db.execute(query).scalars().all()


def create(db:Session, actuator:schemas.Actuator):

    query = insert(models.Actuator).returning(models.Actuator)
    result = db.scalars(query, actuator.model_dump()).first()
    if result is None:
        raise ValueError("Failed to create actuator")
    return result


def update_actuator(db:Session, actuator:schemas.Actuator):
    
    query = (
        update(models.Actuator)
        .where(models.Actuator.actuator_id == actuator.actuator_id)
        .values(**actuator.model_dump())
        .returning(models.Actuator)
    )
    return db.execute(query).scalars().first() 

def update_last_activated(db: Session, actuator_id: int):
    query = (
        update(models.Actuator).
        where(models.Actuator.actuator_id == actuator_id).
        values(last_activated=datetime.now().astimezone()).
        returning(models.Actuator)
    )
    return db.execute(query).scalars().first()
