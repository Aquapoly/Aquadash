from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from . import manager, schemas, models

def create(db: Session, prototype: schemas.Prototype) -> models.Prototype:
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
    try:
        created_prototype = manager.create(db=db, prototype=prototype)
        db.commit()
        db.refresh(created_prototype)
        return created_prototype
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflict in database: {err}",
        )

def get_by_id(db: Session, prototype_id:int) :
    """
    Retrieves prototype from the database, optionally filtered by ID.
    Args:
        db (Session): SQLAlchemy session.
        prototype_id (int | None, optional): If provided, filters prototypes by the given ID.
    Returns:
        list[models.Prototype]: List of prototypes matching the criteria.

    Raises:
        HTTPException: If a database error occurs during the query.
    """
    
    prototypes = manager.get_by_id(db=db, prototype_id=prototype_id)
    if(len(prototypes) == 0) : 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prototype Id {prototype_id} does not exist",
        )
    return prototypes

def get_all(db:Session):
    return manager.get_all(db=db)


