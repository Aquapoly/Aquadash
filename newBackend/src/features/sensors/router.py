
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database.database import get_db
from . import service, schemas

router = APIRouter(prefix="/sensors", tags=["Sensors"])

@router.post("/", response_model=schemas.Sensor)
async def post(
    sensor: schemas.SensorBase, 
    db: Session = Depends(get_db)
):
    return service.create(
        db=db,
        sensor=sensor,
    )


@router.get("/{prototype_id}", response_model=list[schemas.Sensor])
async def get(
    prototype_id: int,
    db: Session = Depends(get_db),
):
    return service.get_sensors(db=db, prototype_id=prototype_id)


@router.patch(
    "/",
    dependencies=[],
    response_model=list[schemas.Sensor]
)
async def patch(
    sensors: list[schemas.Sensor],
    db: Session = Depends(get_db),
):
    return service.update_sensors(db=db, sensors=sensors)