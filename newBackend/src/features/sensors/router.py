
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database.database import get_db
from .schemas import Sensor, SensorBase
from . import service

router = APIRouter(prefix="/sensors", tags=["Sensors"])

@router.post("/", response_model=Sensor)
async def post(
    sensor: SensorBase, 
    db: Session = Depends(get_db)
):
    return service.create(
        db=db,
        sensor=sensor,
    )


@router.get("/{prototype_id}", response_model=list[Sensor])
async def get(
    prototype_id: int,
    db: Session = Depends(get_db),
):
    return service.get_sensors(db=db, prototype_id=prototype_id)