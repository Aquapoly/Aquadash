from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from ..database.database import get_db
from . import service, schemas, authentication

router = APIRouter(prefix="/users", tags=["Users"])




# auth stuff
@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = authentication.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    authentication.log_in(db, form_data.username)
    access_token_expires = timedelta(
        minutes=authentication.USER_ACCESS_TOKEN_EXPIRATION
    )
    access_token = authentication.create_access_token(
        data={"user": user.username, "permissions": user.permissions},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "Bearer"}


@router.post("/new/", response_model=schemas.Token)
async def create_user_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    try:
        crud.post_user(db, form_data.username, form_data.password)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="username already exists",
        ) from exc
    return await login_for_access_token(form_data, db)


@router.post("/logout/")
async def user_log_out(
    token: Annotated[str, Depends(authentification.oauth2_scheme)],
    db: Session = Depends(get_db),
):
    permissions.verify_token(token, db)
    username = permissions.dict_from_token(token)["user"]
    authentification.log_out(db, username)
    return status.HTTP_200_OK


# for some reason we need to keep this here to keep the authorization header button in /docs
@router.get("/items/")
async def read_items(token: Annotated[str, Depends(authentication.oauth2_scheme)]):
    return {"token": token}