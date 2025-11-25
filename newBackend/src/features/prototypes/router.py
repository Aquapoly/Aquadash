from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database.database import get_db
from .schemas import Prototype
from .import service

router = APIRouter(prefix="/prototypes", tags=["Prototypes"])

@router.post("/", response_model= Prototype)
def post(
    prototype: Prototype,
    db: Session = Depends(get_db)
):
    return service.create(db=db, prototype=prototype)


@router.get("/{prototype_id}", response_model=list[Prototype])
async def get(
    prototype_id: int,
    db: Session = Depends(get_db)
):
    return service.get_prototypes(db=db, prototype_id=prototype_id)
