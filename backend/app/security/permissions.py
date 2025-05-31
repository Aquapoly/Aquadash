from jose import JWTError, jwt
from . import authentification
from fastapi import HTTPException, status, Depends
import math
import time
from sqlalchemy.orm import Session
from .. import models
from typing import Annotated
from app.database import get_db


POST_MEASURMENTS_PERMISSION = 2**0
GET_MEASURMENTS_PERMISSION = 2**1
MODIFY_SENSOR_AND_PROTOTYPES_PERMISSION = 2**2

# tokens do nothing in code. I just have nowhere to put them
POST_MEASURMENTS_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwZXJtaXNzaW9ucyI6MSwiZXhwIjoxNzAwNTk4MDcxfQ.mZbCxkeEgL-qGBI1C1RIXslRf_Vi6lkVUH8zMMxCgu4",
)
GET_MEASURMENTS_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwZXJtaXNzaW9ucyI6MiwiZXhwIjoxNzAwNTk4MDcxfQ.IZq-5i2NXYmWM-m3l6sL1BRBQ3S6pdKo7-TkYh3pSH8",
)
MODIFY_SENSOR_AND_PROTOTYPES_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwZXJtaXNzaW9ucyI6NCwiZXhwIjoxNzAwNTk4MDcxfQ.xHWb6XR31IlapiMbXoRnbBAJuK2mBeN-ZkNeK-enpNM",
)

TOKEN_NOT_AUTHORIZED_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="token does not have the required permissions for this action",
)

TOKEN_EXPIRED_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="token has expired",
)

TOKEN_INVALID_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="token is invalid",
)


class Permissions:
    post_measurment: bool = False
    get_measurment: bool = False
    modifify_sensors_and_prototype: bool = False

    def __init__(self, encoded: None | int = None):
        if encoded == None:
            return
        self.post_measurment = (
            math.floor(encoded / POST_MEASURMENTS_PERMISSION)
        ) % 2 > 0
        self.get_measurment = (math.floor(encoded / GET_MEASURMENTS_PERMISSION)) % 2 > 0
        self.modifify_sensors_and_prototype = (
            math.floor(encoded / MODIFY_SENSOR_AND_PROTOTYPES_PERMISSION)
        ) % 2 > 0

    def encode_to_int(self) -> int:
        return (
            POST_MEASURMENTS_PERMISSION * self.post_measurment
            + GET_MEASURMENTS_PERMISSION * self.get_measurment
            + MODIFY_SENSOR_AND_PROTOTYPES_PERMISSION
            * self.modifify_sensors_and_prototype
        )


def verify_token(
    token: str,
    db: Session,
    needs_perm_post_measure=False,
    needs_perm_get_measure=False,
    needs_perm_modify_proto=False,
):
    """
    Vérifie la validité du token, les permissions requises et si l'utilisateur est connecté.
    Args:
        token (str): Le token JWT à vérifier.
        db (Session): Session SQLAlchemy pour accéder à la base de données.
        needs_perm_post_measure (bool): Permission requise pour poster une mesure.
        needs_perm_get_measure (bool): Permission requise pour obtenir une mesure.
        needs_perm_modify_proto (bool): Permission requise pour modifier un capteur ou un prototype.
    Raises:
        TOKEN_EXPIRED_ERROR: Si le token a expiré ou si l'utilisateur n'est pas connecté.
        TOKEN_INVALID_ERROR: Si le token est invalide.
        TOKEN_NOT_AUTHORIZED_ERROR: Si les permissions sont insuffisantes.
    """
    decoded_token = dict_from_token(token)
    verify_token_permission(
        decoded_token,
        post_measurment_permission_required=needs_perm_post_measure,
        get_measurement_permission_required=needs_perm_get_measure,
        modify_sensor_and_prototype_permission_required=needs_perm_modify_proto,
    )
    verify_token_active(decoded_token, db)


def verify_token_active(token: dict, db: Session):
    """
    Vérifie si le token fourni correspond à un utilisateur actuellement connecté.
    Args:
        token (dict): Dictionnaire contenant les informations du token, dont le nom d'utilisateur sous la clé "user".
        db (Session): Session SQLAlchemy pour accéder à la base de données.
    Raises:
        TOKEN_EXPIRED_ERROR: Si l'utilisateur correspondant au token n'est pas connecté (logged_in est False).
    """
    username = token["user"]
    if username is None:
        return
    user = db.query(models.User).filter_by(username=username).first()
    if not user.logged_in:
        raise TOKEN_EXPIRED_ERROR


def verify_token_permission(
    token: dict,
    post_measurment_permission_required: bool,
    get_measurement_permission_required: bool,
    modify_sensor_and_prototype_permission_required: bool,
) -> bool:
    """
    Vérifie si le token fourni possède les permissions nécessaires pour effectuer une action.
    Args:
        token (dict): Dictionnaire contenant les informations du token, dont les permissions sous la clé "permissions".
        post_measurment_permission_required (bool): Permission requise pour poster une mesure.
        get_measurement_permission_required (bool): Permission requise pour obtenir une mesure.
        modify_sensor_and_prototype_permission_required (bool): Permission requise pour modifier un capteur ou un prototype.
    Raises:
        TOKEN_NOT_AUTHORIZED_ERROR: Si le token ne possède pas les permissions nécessaires.
    """
    permission_code = token["permissions"]
    perm = Permissions(permission_code)
    if (
        (post_measurment_permission_required and not perm.post_measurment)
        or (get_measurement_permission_required and not perm.get_measurment)
        or (
            modify_sensor_and_prototype_permission_required
            and not perm.modifify_sensors_and_prototype
        )
    ):
        raise TOKEN_NOT_AUTHORIZED_ERROR


def dict_from_token(token: str) -> dict:
    """
    Décode un token JWT en dictionnaire et gère les erreurs courantes.
    Args:
        token (str): Le token JWT à décoder.
    Returns:
        dict: Le contenu décodé du token.
    Raises:
        TOKEN_EXPIRED_ERROR: Si le token a expiré.
        TOKEN_INVALID_ERROR: Si le token est invalide.
        HTTPException: Pour toute autre erreur lors du décodage.
    """
    try:
        return jwt.decode(
            token,
            authentification.SECRET_KEY,
            algorithms=authentification.ALGORITHM,
            options={
                "verify_signature": True,
            },
        )
    except jwt.ExpiredSignatureError as exc:
        raise TOKEN_EXPIRED_ERROR from exc
    except jwt.InvalidSignatureError as exc:
        raise TOKEN_INVALID_ERROR from exc
    except Exception as exc:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR) from exc


def needs_prototype_modification_permission(
    token: Annotated[str, Depends(authentification.oauth2_scheme)],
    db: Session = Depends(get_db),
):
    """
    Dependency that verifies if the current user, identified by the provided OAuth2 token,
    has permission to modify prototypes. Raises an exception if the user lacks the required permission.
    Args:
        token (str): OAuth2 token extracted from the request.
        db (Session): SQLAlchemy database session.
    Raises:
        HTTPException: If the token is invalid or the user does not have prototype modification permissions.
    """
    verify_token(token, db, needs_perm_modify_proto=True)


def needs_measurements_post_permission(
    token: Annotated[str, Depends(authentification.oauth2_scheme)],
    db: Session = Depends(get_db),
):
    """
    Dependency that verifies if the current user, identified by the provided OAuth2 token,
    has permission to post measurements. Raises an exception if the user lacks the required permission.
    Args:
        token (str): OAuth2 token extracted from the request.
        db (Session): SQLAlchemy database session.
    Raises:
        HTTPException: If the token is invalid or the user does not have post measurement permissions.
    """
    verify_token(token, db, needs_perm_post_measure=True)


def needs_measurements_get_permission(
    token: Annotated[str, Depends(authentification.oauth2_scheme)],
    db: Session = Depends(get_db),
):
    """
    Dependency that verifies if the current user, identified by the provided OAuth2 token,
    has permission to get measurements. Raises an exception if the user lacks the required permission.
    Args:
        token (str): OAuth2 token extracted from the request.
        db (Session): SQLAlchemy database session.
    Raises:
        HTTPException: If the token is invalid or the user does not have get measurement permissions.
    """
    verify_token(token, db, needs_perm_get_measure=True)
