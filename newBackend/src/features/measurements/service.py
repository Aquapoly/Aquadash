from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound

from . import repository, schemas, models


def create(db: Session, measurement: schemas.MeasurementBase):
    """
    Inserts a new measurement into the database.
    Args:
        db (Session): SQLAlchemy session.
        measurement (schemas.MeasurementBase): Validated measurement data to add to the DB.
    Returns:
        models.Measurement: The created measurement.
    Raises:
        HTTPException: On integrity error (e.g., sensor does not exist), raises 422 with details.
    """
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