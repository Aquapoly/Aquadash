
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from . import service, schemas
from ..database.database import get_db

router = APIRouter(prefix="/sensors", tags=["Sensors"])

@router.post(
    "/", 
    response_model=schemas.Sensor,
    status_code=status.HTTP_201_CREATED,
)
async def post(
    sensor: schemas.Sensor, 
    db: Session = Depends(get_db),
):
    return service.create(db=db,sensor=sensor)

@router.get(
        "/",
        response_model=list[schemas.Sensor]
)
async def get_all(
    db: Session = Depends(get_db),
):
    return service.get_all(db=db)

@router.get(
    "/{prototype_id}", 
    response_model=list[schemas.Sensor],
)
async def get(
    prototype_id: int,
    db: Session = Depends(get_db),
):
    return service.get(db=db, prototype_id=prototype_id)


@router.patch(
    "/",
    dependencies=[],
    response_model=list[schemas.Sensor]
)
async def patch(
    sensors: list[schemas.Sensor],
    db: Session = Depends(get_db),
):
    return service.update_multiple(db=db, sensors=sensors)