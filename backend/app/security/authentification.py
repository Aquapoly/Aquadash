from passlib.context import CryptContext
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from .. import schemas
from sqlalchemy.orm import Session
from .. import models

SECRET_KEY = "d1c7fa9d4f8dc8d8731896337e1131ef586e6f0f7f5b7af4554adba5efdb7c0d"
ALGORITHM = "HS256"
USER_ACCESS_TOKEN_EXPIRATION = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Vérifie si le mot de passe fourni correspond au hash stocké (avec sel).
def verify_password(plain_password: str, salt: str, hashed_password: str):
    return pwd_context.verify(plain_password + salt, hashed_password)

# Retourne le hash du mot de passe fourni.
def get_password_hash(password):
    return pwd_context.hash(password)

# Récupère un utilisateur par nom d'utilisateur.
def get_user(db: Session, username: str):
    return db.query(models.User).filter_by(username=username).first()

# Marque l'utilisateur comme connecté.
def log_in(db: Session, username: str):
    db.query(models.User).filter_by(username=username).update(
        {models.User.logged_in: True}
    )
    db.commit()

# Marque l'utilisateur comme déconnecté.
def log_out(db: Session, username: str):
    db.query(models.User).filter_by(username=username).update(
        {models.User.logged_in: False}
    )
    db.commit()

# Authentifie un utilisateur avec nom d'utilisateur et mot de passe.
def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.pw_salt, user.pw_hash):
        return False
    return user

# Crée un Json Web Token d'accès pour l'utilisateur.
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
