from . import schemas, service

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database.database import get_db

router = APIRouter(prefix="/Measurements", tags=["Measurements"])

@router.post("/", response_model=schemas.Measurement)
async def post(
    measurement: schemas.MeasurementBase,
    db: Session = Depends(get_db),
):
    return service.create(
        db=db, 
        measurement=measurement,
    )
