from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from . import models, schemas


def create(db: Session, prototype: schemas.Prototype) -> models.Prototype | None:
    """
    Inserts a new prototype into the database.

    Args:
        db (Session): SQLAlchemy session.
        prototype (schemas.Prototype): Prototype data to add.

    Returns:
        models.Prototype | None: The created prototype object, or None if creation fails.
    """
    query = (
        insert(models.Prototype)
        .values(prototype.model_dump())
        .returning(models.Prototype)
    )
    return db.execute(query).scalars().first()

def get_by_id(db:Session, prototype_id:int):
    query = (
        select(models.Prototype)
        .where(models.Prototype.prototype_id == prototype_id)
    )
    return db.execute(query).scalars().first()

def get_all(db:Session):
    query = select(models.Prototype)
    return db.execute(query).scalars().all()