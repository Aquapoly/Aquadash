from sqlalchemy.orm import Session
from . import models


def get_user(db: Session, username: str):
    return db.query(models.User).filter_by(username=username).first()


def insert_user(db: Session, user: models.User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_logged_in(db: Session, username: str):
    db.query(models.User).filter_by(username=username).update(
        {models.User.logged_in: True}
    )
    db.commit()


def set_logged_out(db: Session, username: str):
    db.query(models.User).filter_by(username=username).update(
        {models.User.logged_in: False}
    )
    db.commit()

def is_user_logged_in(db: Session, username: str) -> bool:
    user = (
        db.query(models.User.logged_in)
        .filter_by(username=username)
        .first()
    )
    if user is None:
        return False
    return True