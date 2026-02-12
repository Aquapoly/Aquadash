from sqlalchemy import insert
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
        .values(**prototype.model_dump())
        .returning(models.Prototype)
    )
    return db.execute(query).scalars().first()
