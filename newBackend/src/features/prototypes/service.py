from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from . import repository, schemas, models

def create(db: Session, prototype: schemas.Prototype) -> models.Prototype:

    try:
        created_prototype = repository.create(db=db, prototype=prototype)
        # The repository returns None if the insert fails in a way that doesn't raise an exception,
        # which can happen with 'returning'. We'll treat that as a conflict or bad data.
        if created_prototype is None:
            raise IntegrityError

        db.commit()
        db.refresh(created_prototype)
        return created_prototype
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflict in database: {err}",
        )

def get_prototype(db: Session, prototype_id:int) :
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
    if(prototype_id == None): return repository.get_all(db=db)
    prototypes = repository.get_by_id(db=db, prototype_id=prototype_id)
    if(len(prototypes) == 0) : 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prototype Id {prototype_id} does not exist",
        )
    return prototypes