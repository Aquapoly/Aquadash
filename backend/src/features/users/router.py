from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from ..database.database import get_db
from . import service, schemas, auth_utils

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/token", response_model=schemas.Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    return await service.login(db, form_data)


@router.post(
    "/new/",
    response_model=schemas.Token,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    return await service.create_user(db, form_data)


@router.post("/logout/")
async def logout(
    token: Annotated[str, Depends(auth_utils.oauth2_scheme)],
    db: Session = Depends(get_db),
):
    return service.logout(db, token)



# required for Swagger auth button
@router.get("/items/")
async def read_items(
    token: Annotated[str, Depends(auth_utils.oauth2_scheme)]
):
    return {"token": token}