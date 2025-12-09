import csv
from io import StringIO
from sqlalchemy.orm import Session
from app import models



def export_all_measures_to_csv(db_session: Session):
    """
    Exports all measurements from all sensors into a CSV string sorted by sensor.
    Args:
        db_session (Session): SQLAlchemy session used to query the Sensor and Measurement tables.
    Returns:
        str: CSV content with columns
             ["Sensor ID", "Sensor Type", "Sensor Value", "Timestamp",
              "Threshold Critically Low", "Threshold Low", "Threshold High", "Threshold Critically High"].
    Raises:
        sqlalchemy.exc.SQLAlchemyError: If a database error occurs during queries.
        AttributeError: If a sensor referenced by a measurement lacks the expected threshold attributes.
    """
    
    sensor_ids = db_session.query(models.Sensor.sensor_id).distinct().all()
    csv_output = StringIO()
    csv_writer = csv.writer(csv_output)
    csv_writer.writerow([
        "Sensor ID", "Sensor Type", "Sensor Value", "Timestamp",
        "Threshold Critically Low", "Threshold Low", "Threshold High", "Threshold Critically High"
    ])

    for sensor_id_tuple in sensor_ids:
        sensor_id = sensor_id_tuple[0]
        response = db_session.query(models.Measurement).filter_by(sensor_id=sensor_id)
        sensor = db_session.query(models.Sensor).filter_by(sensor_id=sensor_id).first()
        threshold_critically_low = sensor.threshold_critically_low
        threshold_low = sensor.threshold_low
        threshold_high = sensor.threshold_high
        threshold_critically_high = sensor.threshold_critically_high

        for measurement in response:
            sensor_type = db_session.query(models.Sensor).filter_by(sensor_id=measurement.sensor_id).first().sensor_type.name
            csv_writer.writerow([
                sensor_id, sensor_type, measurement.value, measurement.timestamp,
                threshold_critically_low, threshold_low, threshold_high, threshold_critically_high
            ])

    csv_content = csv_output.getvalue()
    csv_output.close()
    return csv_content