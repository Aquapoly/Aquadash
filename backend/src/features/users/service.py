
import secrets
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from . import manager, models, permissions, auth_utils


async def login(db: Session, form: OAuth2PasswordRequestForm):
    user = manager.get_user(db, form.username)

    if not user or not auth_utils.verify_password(
        form.password, user.pw_salt, user.pw_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    manager.set_logged_in(db, user.username)

    token = auth_utils.create_access_token(
        {
            "user": user.username,
            "permissions": user.permissions,
        },
        timedelta(minutes=auth_utils.USER_ACCESS_TOKEN_EXPIRATION),
    )

    return {"access_token": token, "token_type": "Bearer"}


async def create_user(db: Session, form: OAuth2PasswordRequestForm):
    if manager.get_user(db, form.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username already exists",
        )

    perm = permissions.Permissions()
    perm.modifify_sensors_and_prototype = True
    perm.get_measurment = True

    salt = secrets.token_hex(128)
    hashed = auth_utils.get_password_hash(form.password + salt)

    user = models.User(
        username=form.username,
        pw_salt=salt,
        pw_hash=hashed,
        permissions=perm.encode_to_int(),
        logged_in=True,
    )

    manager.insert_user(db, user)

    return await login(db, form)



def logout(db: Session, token: str):

    permissions.verify_token(token, db)

    payload = permissions.dict_from_token(token)
    username = payload["user"]

    manager.set_logged_out(db, username)

    return status.HTTP_200_OK