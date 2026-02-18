from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound

from datetime import datetime, timedelta
from pytz import UTC

from . import manager, schemas, models, activation_condition
from ..sensors.manager import get_by_prototype as get_sensors
from ..measurements.service import get_last as get_last_measurement
from ..measurements.models import Measurement

DISCONNECTED_DELTA = timedelta(days=1)



def get_by_prototype(db: Session, prototype_id: int):
    """
    Retrieves all actuators associated with the sensors of a given prototype.
    Args:
        db (Session): SQLAlchemy session.
        prototype_id (int): The ID of the prototype whose actuators are to be fetched.
    Returns:
        list[models.Actuator]: List of actuators linked to the sensors of the specified prototype.
    Raises:
        HTTPException: If the prototype_id does not exist, raises 404 with details.
    """
    sensor_ids: list[int] = [
        sensor.sensor_id for sensor in get_sensors(db=db, prototype_id=prototype_id)
    ]
    actuator = manager.get_by_prototype(db=db, sensor_ids=sensor_ids)
    if(len(actuator) == 0):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No actuator is associated with the Prototype Id {prototype_id}"
        )
    return actuator



def get_by_id(db: Session, actuator_id: int):
    """
    Retrieves an actuator from the database by its ID.
    Args:
        db (Session): SQLAlchemy session.
        actuator_id (int): The unique identifier of the actuator to retrieve.
    Returns:
        models.Actuator | None: The actuator instance if found, otherwise None.
    Raises:
        HTTPException: On no actuator id, raises 400 with details.
    """
    

    if not actuator_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Must enter an Id"
        )
    
    actuator = manager.get(db, actuator_id)

    if actuator is None:
            raise HTTPException(status_code=404, detail="Actuator with this ID not found")
    last_measurement = get_last_measurement(db=db, sensor_id=actuator.sensor_id)

    return get_actuator_activation(actuator, last_measurement)


def create(db: Session, actuator: schemas.Actuator):
    """
    Inserts a new actuator into the database.
    Args:
        db (Session): SQLAlchemy session.
        actuator (schemas.ActuatorBase): Validated actuator data to add to the DB.
    Returns:
        models.Actuator: The created actuator.
    Raises:
        HTTPException: On integrity error (e.g., duplicate), raises 409 with details.
    """
    
    try:
        created = manager.create(db=db, actuator=actuator)
        db.commit()
        db.refresh(created)
        return created
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error from db: {err}",
        )
    

def update(db: Session, actuator: schemas.Actuator):
    """
    Updates an existing actuator in the database.
    Args:
        db (Session): SQLAlchemy session.
        actuator (schemas.Actuator): Validated actuator data to update in the DB.
    Returns:
        models.Actuator: The updated actuator.
    Raises:
        HTTPException: If an integrity error occurs (e.g., constraint violation), raises 422 with details.
        HTTPException: If the actuator_id does not exist, raises 400 with details.
    """

    try:
        updated_actuator = manager.update_actuator(db=db, actuator=actuator)
        if updated_actuator is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Received an actuator with non existant actuator_id {actuator.actuator_id}",
            )
        db.commit()
        db.refresh(updated_actuator)
        return updated_actuator
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Integrity error in db: {err}",
        )
    

def update_multiple(db: Session, actuators: list[schemas.Actuator]):
    """
    Updates multiple actuators in the database.
    Args:
        db (Session): SQLAlchemy session.
        actuators (list[schemas.Actuator]): List of validated actuator data to update in the DB.
    Returns:
        list[models.Actuator]: List of updated actuator objects.
    Raises:
        HTTPException: If an actuator update fails, raises an appropriate HTTPException with details.
    """
    updated_actuators = []
    for actuator in actuators:
        updated_actuators.append(update(db, actuator))
    return updated_actuators


def update_last_activated(db: Session, actuator_id: int):
    """
    Updates the 'last_activated' timestamp of a specific actuator in the database.
    Args:
        db (Session): SQLAlchemy session.
        actuator_id (int): The unique identifier of the actuator to update.
    Returns:
        models.Actuator: The updated actuator instance.
    Raises:
        HTTPException: If an integrity error occurs during the update (422) or if the actuator_id does not exist (400).
    """
    
    try:
        updated_actuator = manager.update_last_activated(db=db, actuator_id=actuator_id)
        if updated_actuator is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Received an actuator with non existant actuator_id {actuator_id}",
            )
        db.commit()
        db.refresh(updated_actuator)
        return updated_actuator
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Integrity error in db: {err}",
        )
    

def get_actuator_activation(actuator: schemas.Actuator, last_measurement: (Measurement | None)): 
    """
    Determines whether an actuator should be activated based on its configuration and the latest measurement.
    Args:
        actuator (schemas.Actuator): The actuator configuration and state.
        last_measurement (models.Measurement | None): The most recent measurement associated with the actuator, or None if no measurement exists.
    Returns:
        schemas.ActuatorActivation: An object indicating whether to activate the actuator, the activation status message, duration, and period.
    Raises:
        None
    """
  
    if(not actuator.enabled):
        status = "L'actuateur est désactivé."
        return schemas.ActuatorActivation(
            activate=False, 
            status=status, 
            duration=actuator.activation_duration,
            period=actuator.activation_period
        )
    
    if (last_measurement is None):
        status = "Le capteur n'a enregistré aucune mesure."
        return schemas.ActuatorActivation(
            activate=False, 
            status=status, 
            duration=actuator.activation_duration, 
            period=actuator.activation_period
        )
    
    # TODO: réfléchir si ce serait pertinent de rajouter une vérification que la mesure
    # n'est pas en dehors du "threshold_critically_high" et "threshold_critically_low",
    # ce qui  pourrait signifier une valeur incorrigible (ou abhérante! ex. EC négatif)

    now = datetime.now().astimezone()
    last_measure_time_elapsed = now - last_measurement.timestamp

    if(last_measure_time_elapsed > DISCONNECTED_DELTA):
        status = "La dernière mesure est trop vieille, le capteur est possiblement déconnecté."
        return schemas.ActuatorActivation(
            activate=False, 
            status=status, 
            duration=actuator.activation_duration, 
            period=actuator.activation_period
        )

    last_activation_time_elapsed = now - actuator.last_activated

    if(last_activation_time_elapsed < timedelta(seconds=actuator.activation_period)):
        return schemas.ActuatorActivation(
            activate=False, 
            status="La période d'activation ne s'est pas encore écoulée.", 
            duration=actuator.activation_duration, 
            period=actuator.activation_period
        )

    activate = activation_condition.activation_map[
        actuator.activation_condition
    ](last_measurement.value, actuator.condition_value)

    return schemas.ActuatorActivation(
        activate=activate, 
        status="OK", 
        duration=actuator.activation_duration, 
        period=actuator.activation_period
    )
