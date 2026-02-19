
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from . import schemas, service
from ..database.database import get_db

router = APIRouter(prefix="/actuators", tags=["Actuators"])

### OK
@router.get(
    "/prototype/{prototype_id}",
    response_model=list[schemas.Actuator],
)
async def actuator(prototype_id: int, db: Session = Depends(get_db)):
    return service.get_by_prototype(db=db, prototype_id=prototype_id)


@router.get(
        "/{actuator_id}/state",
        dependencies=[],
        response_model=schemas.ActuatorActivation,
)
async def get_state(
    actuator_id: int,
    db: Session = Depends(get_db)
):
    return service.get_by_id(db=db, actuator_id=actuator_id)
    
### OK
@router.post(
    "/",
    dependencies=[],
    response_model=schemas.Actuator,
)
async def post_actuator(
    actuator: schemas.Actuator,
    db: Session = Depends(get_db),
):
    return service.create(db=db, actuator=actuator)

### ok
@router.patch(
    "/",
    dependencies=[],
    response_model=list[schemas.Actuator],
)
async def update_actuators(
    actuators: list[schemas.Actuator],
    db: Session = Depends(get_db),
):
    return service.update_multiple(db=db, actuators=actuators)

### ok
@router.patch(
        "/{actuator_id}/last_activated",
        dependencies=[],
        response_model=schemas.Actuator,
)
async def update_last_activated(actuator_id: int, db: Session = Depends(get_db)):
    return service.update_last_activated(db=db, actuator_id=actuator_id)
