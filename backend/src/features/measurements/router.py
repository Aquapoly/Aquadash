from . import schemas, service, models

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..database.database import get_db

router = APIRouter(prefix="/measurements", tags=["Measurements"])


@router.post(
        "/", 
        response_model=schemas.Measurement)
async def post(
    measurement: schemas.Measurement,
    db: Session = Depends(get_db),
):
    return service.create(db=db, measurement=measurement)


@router.get(
        "/datetime/{sensor_id}",
        response_model=list[schemas.Measurement],
)
async def get(
    sensor_id:int, 
    start_time: datetime | None = None, 
    end_time: datetime | None = None,  
    db: Session = Depends(get_db)
):
    return service.get(
        db=db,
        sensor_id=sensor_id,
        start_time=start_time,
        end_time=end_time
    )


@router.get(
    "/delta/{sensor_id}",
    response_model=list[schemas.Measurement],
)
async def get_by_delta(
    sensor_id:int, 
    time_delta: str = str(timedelta(days=365)).replace(" days", "d"),
    db: Session = Depends(get_db)
):  
    return service.get_by_delta(db=db, sensor_id=sensor_id, time_delta=time_delta)



@router.get(
    "/{sensor_id}/last",
    response_model=schemas.Measurement,
)
async def get_last(
    sensor_id: int, 
    db: Session = Depends(get_db)
):
    return service.get_last(db, sensor_id)



@router.post(
    "/random"
)
async def post_random(
   
    datas:schemas.RandomMeasurements,
    db: Session = Depends(get_db)
):
    return service.post_random(db, datas)