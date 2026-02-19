from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

import random, pytz
from concurrent.futures import ThreadPoolExecutor

from . import manager, schemas, models
from ..sensors.models import Sensor as sensor_model


def create(db: Session, measurement: schemas.Measurement):
    """
    Inserts a new measurement into the database.
    Args:
        db (Session): SQLAlchemy session.
        measurement (schemas.MeasurementBase): Validated measurement data to add to the DB.
    Returns:
        models.Measurement: The created measurement.
    Raises:
        HTTPException: On integrity error (e.g., sensor does not exist), raises 422 with details.
    """
    
    try:
        created = manager.create(db=db, measurement=measurement)
        db.commit()
        db.refresh(created)
        return created
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Sensor with this id does not exist",
        )


def get(
    db: Session,
    sensor_id: int,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
):
    """
    Retrieves measurements for a given sensor within an optional time range.
    Args:
        db (Session): SQLAlchemy session.
        sensor_id (int): ID of the sensor to retrieve measurements for.
        start_time (datetime, optional): Start of the time range (exclusive). Defaults to None.
        end_time (datetime, optional): End of the time range (exclusive). Defaults to None.
    Returns:
        list[models.Measurement]: List of measurements matching the criteria.
        
    """
    try:
        if not start_time and not end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No start_time or end time where given"
            )
        measurements = manager.get(db=db, sensor_id=sensor_id, start_time=start_time, end_time=end_time)
        # if not measurements:
        #     raise Exception
        return measurements
    except Exception as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error in database: {err}"
        )


def get_by_delta(
    db: Session,
    sensor_id: int,
    time_delta: str,
):
    """
    Retrieves measurements for a given sensor within a specified time delta.
    Args:
        db (Session): SQLAlchemy session.
        sensor_id (int): ID of the sensor to retrieve measurements for.
        time_delta (datetime): Time interval to look back from the current time.
    Returns:
        List[models.Measurement]: List of measurements within the specified time delta.
    Raises:
        None
    """
    # Parse "365d,00:00:00" ou "365" (jours) selon ton format
    try:
        days, time_part = time_delta.split(",")
        days = int(days.replace("d", ""))
        h, m, s = map(int, time_part.split(":"))
        delta = timedelta(days=days, hours=h, minutes=m, seconds=s)
    except Exception:
        raise HTTPException(status_code=400, detail="Format time_delta invalide. Attendu: '365d,00:00:00'")

    end_time = datetime.now()
    start_time = end_time - delta
    return get(db=db, sensor_id=sensor_id, start_time=start_time, end_time=end_time)


def get_last(
    db: Session,
    sensor_id: int,
):
    """
    Retrieves the most recent measurement for a given sensor from the database.
    Args:
        db (Session): SQLAlchemy session.
        sensor_id (int): The ID of the sensor whose latest measurement is requested.
    Returns:
        models.Measurement | None: The latest measurement for the sensor, or None if not found.
    """
    measurement = manager.get_last(db=db, sensor_id=sensor_id)
    if measurement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor ID has no measurements.")
    return measurement

def generate_smooth_values(middle:float,rnge:float, nb_meas:int, alpha:float, threshold:float, drift_adjustment:float):
    """
    Generates a list of smoothed random values based on a Gaussian distribution and smoothing parameters.
    Args:
        middle (float): The mean value around which to generate measurements.
        rnge (float): The standard deviation for the Gaussian distribution.
        nb_meas (int): The number of measurements to generate.
        alpha (float): Smoothing factor (between 0 and 1) for exponential smoothing.
        threshold (float): Maximum allowed change between consecutive smoothed values.
        drift_adjustment (float): Factor to adjust drift towards the mean.
    Returns:
        list[float]: List of smoothed and threshold-limited random values.
    """
    values = []
    drift_adjustment = 0.20
    values.append(round(random.gauss(middle,rnge), 2))
    for i in range(1, nb_meas):
        new_val = round(random.gauss(middle,rnge),2) + drift_adjustment*(middle-values[i-1])*0.5
        smooth_value = alpha*new_val + (1-alpha)*values[i-1]
        if abs(smooth_value - values[i-1]) > threshold:
            smooth_value = values[i-1] - threshold if smooth_value < values[i-1] else values[i-1] + threshold
        values.append(round(smooth_value,2))
    return values

def generate_timestamps(nb_meas:int, rnge:str):
    """
    Generates a sorted list of random timestamps within a specified time range.
    Args:
        nb_meas (int): Number of timestamps to generate.
        rnge (str): Time range for the timestamps. Accepted values are "year", "day", or "hour".
    Returns:
        list: Sorted list of string representations of randomly generated timestamps within the specified range.
    Raises:
        ValueError: If the provided range is not one of "year", "day", or "hour".
    """
    timestamps = []
    for i in range(nb_meas):
        now = datetime.now(pytz.UTC)
        if   rnge == "year": startingDate = now - timedelta(days=365)
        elif rnge == "day": startingDate = now - timedelta(days=1)
        elif rnge == "hour" : startingDate = now - timedelta(hours=1)
        delta     = now-startingDate
        timestamp =  startingDate + timedelta(seconds=random.randint(0, int(delta.total_seconds())))
        timestamps.append(f"'{timestamp}'")
    sorted_copy = sorted(timestamps.copy())
    return sorted_copy


def generate(db:Session, datas:schemas.RandomMeasurements):
    """
    Generates synthetic measurement data for all sensors in the database, distributing measurements across yearly, daily, and hourly intervals.
    Args:
        nb_meas (int): Total number of measurements to generate (will be adjusted to be divisible by the number of sensors).
        year_ratio (float): Proportion of measurements to assign to the yearly interval.
        day_ratio (float): Proportion of measurements to assign to the daily interval.
        hour_ratio (float): Proportion of measurements to assign to the hourly interval.
        deviation_percent (float): Percentage of deviation to apply to the generated values.
        smoothing_factor (float): Factor controlling the smoothness of the generated values.
        drift_adjustment (float): Adjustment factor for value drift over time.
        db (Session): SQLAlchemy session for database access.
    Returns:
        list: A list of lists, each containing [sensor_id, value, timestamp] for each generated measurement.
    Raises:
        ValueError: If the number of sensors in the database is zero.
    """
    request = db.query(sensor_model).all()
    nb_sensors = len(request)
    nb_meas = datas.nb_measurements
    while nb_meas % nb_sensors != 0: nb_meas += 1

    nb_year_meas = int(nb_meas * datas.yearly_measurements_ratio)
    nb_day_meas = int(nb_meas * datas.dayly_measurements_ratio)
    nb_hour_meas = int(nb_meas * datas.hourly_measurements_ratio)
    nb_meas_per_sensor = (nb_year_meas + nb_day_meas + nb_hour_meas) // nb_sensors

    def generate_sensor_values(sensor):
        """
        Generates simulated sensor values based on sensor thresholds and configuration parameters.
        Args:
            sensor: An object representing the sensor, expected to have 'threshold_critically_high', 'threshold_critically_low', and 'sensor_id' attributes.
        Returns:
            tuple: A tuple containing the sensor ID and a list of generated smooth values.
        Raises:
            AttributeError: If the sensor object does not have the required attributes.
        """
        value_range = ((sensor.threshold_critically_high - sensor.threshold_critically_low) * datas.deviation_rate / 2)
        middle = (sensor.threshold_critically_high + sensor.threshold_critically_low) / 2
        threshold = value_range / 2
        return sensor.sensor_id, generate_smooth_values(middle, value_range, nb_meas_per_sensor, datas.smoothing_factor, threshold, datas.drift_adjustment)

    with ThreadPoolExecutor() as executor:
        values = dict(executor.map(generate_sensor_values, request))

    timestamps = {
        "year": generate_timestamps(nb_year_meas, "year"),
        "day": generate_timestamps(nb_day_meas, "day"),
        "hour": generate_timestamps(nb_hour_meas, "hour")
    }

    def distribute(nb, time_key):
        """
        Distributes measurement values and timestamps across sensors.
        Args:
            nb (int): Number of measurements to distribute.
            time_key (str): Key to access the relevant timestamps.
        Returns:
            list: A list of lists, each containing [sensor_id, value, timestamp] for each measurement.
        Raises:
            KeyError: If a sensor_id or time_key does not exist in the corresponding dictionary.
            IndexError: If the indices exceed the available values or timestamps.
        """
        index, sensor_index = 0, 0
        result = []
        for i in range(nb):
            result.append([sensor_ids[sensor_index], values[sensor_ids[sensor_index]][index], timestamps[time_key][i]])
            sensor_index += 1
            if sensor_index == nb_sensors:
                index += 1
                sensor_index = 0
        return result

    sensor_ids = list(values.keys())
    return distribute(nb_year_meas, "year") + distribute(nb_day_meas, "day") + distribute(nb_hour_meas, "hour")


def post_random(db:Session, datas:schemas.RandomMeasurements):
    try:
        measurements = generate(db=db, datas=datas)
        manager.delete_all(db=db)
        db.commit()
        for meas in measurements:
            db_Measurement = models.Measurement(sensor_id=meas[0], value=meas[1], timestamp=meas[2])
            new_measurement = manager.add(db=db, measurement=db_Measurement)
            db.commit()
            db.refresh(new_measurement)
        return {"message": "Données remplacées avec succès."}
    except Exception as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))