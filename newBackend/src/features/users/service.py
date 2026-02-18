









from . import permissions


def post_user(db: Session, username: str, password: str):
    """
    Creates and inserts a new user into the database.
    Args:
        db (Session): SQLAlchemy session.
        username (str): Username for the new user.
        password (str): Plaintext password for the new user.
    Returns:
        models.User: The created user instance.
    Raises:
        IntegrityError: If a user with the same username already exists.
    """
    perm = permissions.Permissions()
    perm.modifify_sensors_and_prototype = True
    perm.get_measurment = True
    pw_salt = secrets.token_hex(nbytes=128)
    pw_hash = authentication.get_password_hash(password + pw_salt)
    db_new_user = models.User(
        username=username,
        pw_salt=pw_salt,
        pw_hash=pw_hash,
        permissions=perm.encode_to_int(),
        logged_in=True,
    )
    db.add(db_new_user)
    db.commit()
    db.refresh(db_new_user)
    return db_new_user

