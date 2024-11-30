from app import models, schemas
from app.classes.activation_condition import activation_map

from datetime import datetime, timedelta
from pytz import UTC

DISCONNECTED_DELTA = timedelta(days=1)

def get_actuator_activation(actuator: schemas.Actuator, last_measurement: (models.Measurement | None)): 
    #####
    # Verify validity of actuator and measurement
    #####
    if(not actuator.enabled):
        status = "L'actuateur est désactivé."
        return schemas.ActuatorActivation(
            activate=False, status=status, duration=actuator.activation_duration, period=actuator.activation_period)

    
    if (last_measurement is None):
        status = "Le capteur n'a enregistré aucune mesure."
        return schemas.ActuatorActivation(
            activate=False, status=status, duration=actuator.activation_duration, period=actuator.activation_period)
    
    # TODO: réfléchir si ce serait pertinent de rajouter une vérification que la mesure
    # n'est pas en dehors du "threshold_critically_high" et "threshold_critically_low",
    # ce qui  pourrait signifier une valeur incorrigible (ou abhérante! ex. EC négatif)

    #####
    # Verify elapsed time since last measurement
    #####
    now = datetime.now().astimezone()
    last_measure_time_elapsed = now - last_measurement.timestamp

    if(last_measure_time_elapsed > DISCONNECTED_DELTA):
        status = "La dernière mesure est trop vieille, le capteur est possiblement déconnecté."
        return schemas.ActuatorActivation(
            activate=False, status=status, duration=actuator.activation_duration, period=actuator.activation_period)

    last_activation_time_elapsed = now - actuator.last_activated

    if(last_activation_time_elapsed < timedelta(seconds=actuator.activation_period)):
        # Do not activate if activation_period has not elapsed
        return schemas.ActuatorActivation(
            activate=False, status="La période d'activation ne s'est pas encore écoulée.", duration=actuator.activation_duration, period=actuator.activation_period)

    #####
    # Check if correction needed, using measurement and activation condition
    #####

    activate = activation_map[actuator.activation_condition](
        last_measurement.value, actuator.low, actuator.high)

    return schemas.ActuatorActivation(
        activate=activate, status="OK", duration=actuator.activation_duration, period=actuator.activation_period)
