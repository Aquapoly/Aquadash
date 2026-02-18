from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database.database import get_db

from . import service, schemas

router = APIRouter(prefix="/prototypes", tags=["Prototypes"])

@router.post(
        "/", 
        response_model= schemas.Prototype
)
def post(
    prototype: schemas.Prototype,
    db: Session = Depends(get_db)
):
    return service.create(db=db, prototype=prototype)


@router.get(
        "/{prototype_id}", 
        response_model=list[schemas.Prototype]
)
async def get_by_id(
    prototype_id: int,
    db: Session = Depends(get_db)
):
    return service.get_by_id(db=db, prototype_id=prototype_id)


@router.get(
        "/", 
        response_model=list[schemas.Prototype]
)
async def get_all(
    db: Session = Depends(get_db)
):
    return service.get_all(db=db)