import logging

from fastapi import HTTPException, status
from psycopg import errors as pg_errors
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

# Foreign keys a request can violate, mapped to the request field holding the id and the parent's name.
# Postgres default names: <table>_<column>_fkey.
FOREIGN_KEY_FIELDS = {
    "sensors_prototype_id_fkey": ("prototype_id", "prototype"),
    "actuators_sensor_id_fkey": ("sensor_id", "sensor"),
    "measurements_sensor_id_fkey": ("sensor_id", "sensor"),
}


def _error(status_code: int, loc: list[str], msg: str, error_type: str) -> HTTPException:
    # Same shape as FastAPI's validation errors, so the client handles a single format.
    return HTTPException(
        status_code=status_code,
        detail=[{"loc": loc, "msg": msg, "type": error_type}],
    )


def integrity_error_to_http(err: IntegrityError, values: dict) -> HTTPException:
    """
    Translates a DB integrity error into an HTTPException for the client.
    The raw DB error is logged, not sent: it contains the SQL statement.
    Args:
        err (IntegrityError): The error raised by the insert or update.
        values (dict): The values sent to the DB, used to name the offending id.
    Returns:
        HTTPException: 422 for a missing parent or a check violation, 409 for a unique violation.
    """
    logger.warning("Integrity error in db: %s", err.orig)
    cause = err.orig
    constraint = getattr(getattr(cause, "diag", None), "constraint_name", None)

    if isinstance(cause, pg_errors.ForeignKeyViolation) and constraint in FOREIGN_KEY_FIELDS:
        field, parent = FOREIGN_KEY_FIELDS[constraint]
        return _error(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            ["body", field],
            f"No {parent} with id {values.get(field)}",
            "foreign_key_violation",
        )
    if isinstance(cause, pg_errors.ForeignKeyViolation):
        return _error(
            status.HTTP_422_UNPROCESSABLE_CONTENT, ["body"],
            "References a row that does not exist", "foreign_key_violation",
        )
    if isinstance(cause, pg_errors.CheckViolation):
        return _error(
            status.HTTP_422_UNPROCESSABLE_CONTENT, ["body"],
            f"Violates constraint {constraint}", "check_violation",
        )
    if isinstance(cause, pg_errors.UniqueViolation):
        return _error(
            status.HTTP_409_CONFLICT, ["body"],
            f"Already exists (constraint {constraint})", "unique_violation",
        )
    return _error(
        status.HTTP_422_UNPROCESSABLE_CONTENT, ["body"],
        "Rejected by the database", "integrity_error",
    )
