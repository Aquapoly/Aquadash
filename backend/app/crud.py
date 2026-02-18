from sqlalchemy import and_, insert, select, update
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.classes.activation_condition import ActivationCondition
from app.classes.actuator_type import ActuatorType
from .classes.sensor_type import SensorType

from . import models, schemas
import secrets
from .security import authentification
from .security import permissions
from datetime import datetime, timedelta
import random, pytz
from concurrent.futures import ThreadPoolExecutor



































