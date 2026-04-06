import httpx
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, StreamingResponse
# from fastapi_utils.openapi import simplify_operation_ids
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import datetime, timedelta
import io

from shared.timelapse_models import TimelapseConfig, TimelapseMetadata, TimelapseStatus
# from jose import JWTError, jwt


from . import crud, models, schemas
from .database import engine, get_db
from .classes.sensor_type import SensorType
from .services.actuator import get_actuator_activation
from .services import cam_client as camera_service
from .services.export_data import export_all_measures_to_csv
from .security import authentification
from .security import permissions

models.Base.metadata.create_all(bind=engine)


sensors_data = dict()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = next(get_db())
    crud.default_populate_database(db)
    try:
        yield
    finally:
        try:
            await camera_service.close_client()
        except Exception:
            pass


app = FastAPI(lifespan=lifespan)

origins = ["http://localhost", "http://localhost:4200", "http://127.0.0.1:4200"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post(
    "/prototypes",
    tags=["Prototypes"],
    # dependencies=[Depends(permissions.needs_prototype_modification_permission)],
    response_model=schemas.Prototype,
)
async def post_prototype(
    prototype: schemas.Prototype,
    db: Session = Depends(get_db),
):
    return crud.post_prototype(db=db, prototype=prototype)



@app.post("/sensors/", tags=["Sensors"], response_model=schemas.Sensor)
async def post_sensor(
    sensor: schemas.SensorBase, 
    db: Session = Depends(get_db)
):
    return crud.post_sensor(
        db=db,
        sensor=sensor,
    )

@app.get("/sensors/{prototype_id}", tags=["Sensors"], response_model=list[schemas.Sensor])
async def sensors(
    prototype_id: int,
    db: Session = Depends(get_db),
):
    return crud.get_sensors(db=db, prototype_id=prototype_id)


@app.post(
    "/measurements",
    tags=["Measurements"],
    # dependencies=[Depends(permissions.needs_measurements_post_permission)],
    response_model=schemas.Measurement,
)
async def post_measurement(
    measurement: schemas.MeasurementBase,
    db: Session = Depends(get_db),
):
    return crud.post_measurement(
        db=db, measurement=measurement
    )

@app.post(
    "/actuators",
    tags=["Actuators"],
    dependencies=[],
    response_model=schemas.Actuator,
)
async def post_actuator(
    actuator: schemas.ActuatorBase,
    db: Session = Depends(get_db),
):
    return crud.post_actuator(db=db, actuator=actuator)

@app.patch(
    "/actuators",
    tags=["Actuators"],
    dependencies=[],
    response_model=list[schemas.Actuator],
)
async def update_actuators(
    actuators: list[schemas.Actuator],
    db: Session = Depends(get_db),
):
    return crud.update_actuators(db=db, actuators=actuators)

@app.patch(
    "/sensors",
    tags=["Sensors"],
    dependencies=[],
    response_model=list[schemas.Sensor]
)
async def update_sensors(
    sensors: list[schemas.Sensor],
    db: Session = Depends(get_db),
):
    return crud.update_sensors(db=db, sensors=sensors)

@app.get(
        "/actuators/{actuator_id}/state",
        tags=["Actuators"],
        dependencies=[],
        response_model=schemas.ActuatorActivation,
)
async def get_actuator_state(
    actuator_id: int,
    db: Session = Depends(get_db)
):
    actuator: schemas.Actuator = crud.get_actuator(db=db, actuator_id=actuator_id)
    if actuator is None:
        raise HTTPException(status_code=404, detail="Actuator with this ID not found")
    last_measurement = crud.get_last_measurement(db=db, sensor_id = actuator.sensor_id)

    return get_actuator_activation(actuator, last_measurement)

@app.patch(
        "/actuators/{actuator_id}/last_activated",
        tags=["Actuators"],
        dependencies=[],
        response_model=schemas.Actuator,
)
async def update_actuator_last_activated(actuator_id: int, db: Session = Depends(get_db)):
    return crud.update_actuator_last_activated(db=db, actuator_id=actuator_id)


@app.get("/prototypes", tags=["Prototypes"], response_model=list[schemas.Prototype])
async def prototypes(db: Session = Depends(get_db)):
    return crud.get_prototypes(db=db)

@app.get(
    "/prototypes/{prototype_id}", tags=["Prototypes"], response_model=schemas.Prototype
)
async def prototype(prototype_id: int, db: Session = Depends(get_db)):
    prototype = crud.get_prototypes(db=db, prototype_id = prototype_id)
    if len(prototype) > 0:
        return prototype[0]
    else:
        raise HTTPException(status_code=404, detail="Prototype not found")

@app.get(
    "/measurements/export",
    tags=["Measurements"],
    response_class=StreamingResponse,
)
async def export_all_sensors_to_csv(db: Session = Depends(get_db)):
    csv_content = export_all_measures_to_csv(db)
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=all_sensors_measurements.csv"}
    )

@app.get(
    "/measurements/{sensor_id}",
    tags=["Measurements"],
    response_model=list[schemas.Measurement],
)
async def get_measurement(
    sensor_id:int, time_delta: timedelta | None = None, start_time: datetime | None = None, 
    end_time: datetime | None = None,  db: Session = Depends(get_db)
):
    if time_delta and start_time:
        raise HTTPException(status_code=400, detail="You cannot use both time_delta and start_timestamp")
    
    if time_delta:
        measurements = crud.get_measurements_delta(
            db=db,
            sensor_id=sensor_id,
            time_delta=time_delta,
        )
    else: 
        measurements = crud.get_measurements(
            db=db,
            sensor_id=sensor_id,
            start_time=start_time,
            end_time=end_time,
        )
    return measurements

@app.get(
    "/measurements/{sensor_id}/last",
    tags=["Measurements"],
    response_model=schemas.Measurement,
)
async def get_last_measurement(
    sensor_id: int, db: Session = Depends(get_db)
):
    result = crud.get_last_measurement(db, sensor_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor ID has no measurements.")
    return result


@app.delete(
        "/measurements/{measurement_id}",
        tags=["Measurements"],
)
async def delete_measurement(
    measurement_id: int, db: Session = Depends(get_db)
):
    crud.delete_measurement(db, measurement_id)


@app.get(
    "/actuators/{prototype_id}",
    tags=["Actuators"],
    response_model=list[schemas.Actuator],
)
async def actuator(prototype_id: int, db: Session = Depends(get_db)):
    return crud.get_actuators(db=db, prototype_id=prototype_id)


@app.get("/picture")
async def picture():
    pic: bytes = await camera_service.get_picture()
    return Response(content=pic, media_type="image/jpeg")

# auth stuff
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = authentification.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    authentification.log_in(db, form_data.username)
    access_token_expires = timedelta(
        minutes=authentification.USER_ACCESS_TOKEN_EXPIRATION
    )
    access_token = authentification.create_access_token(
        data={"user": user.username, "permissions": user.permissions},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "Bearer"}


@app.post("/users/new/", response_model=schemas.Token)
async def create_user_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    try:
        crud.post_user(db, form_data.username, form_data.password)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="username already exists",
        ) from exc
    return await login_for_access_token(form_data, db)


@app.post("/users/logout/")
async def user_log_out(
    token: Annotated[str, Depends(authentification.oauth2_scheme)],
    db: Session = Depends(get_db),
):
    permissions.verify_token(token, db)
    username = permissions.dict_from_token(token)["user"]
    authentification.log_out(db, username)
    return status.HTTP_200_OK


# for some reason we need to keep this here to keep the authorization header button in /docs
@app.get("/users/items/")
async def read_items(token: Annotated[str, Depends(authentification.oauth2_scheme)]):
    return {"token": token}

# simplify_operation_ids(app)

@app.post("/Measurement/Random", 
          tags = ["Measurements"])
async def post_random_measurements(
   
    datas:schemas.RandomMeasurements,
    db: Session = Depends(get_db)
):
    try:
        db.query(models.Measurement).delete()
        db.commit()
        return {"message": "Données remplacées avec succès."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        measurements = crud.generate_meas(datas.nb_measurements, 
                                          datas.yearly_measurements_ratio,
                                          datas.dayly_measurements_ratio,
                                          datas.hourly_measurements_ratio, 
                                          datas.deviation_rate, 
                                          datas.smoothing_factor, 
                                          datas.drift_adjustment, db)
        for meas in measurements:
            db_Measurement = models.Measurement(sensor_id=meas[0], value=meas[1], timestamp=meas[2])
            db.add(db_Measurement)
            db.commit()
            db.refresh(db_Measurement)

@app.get(
    "/docs/openapi.json",
    tags=["Docs"],
    summary="OpenAPI JSON",
    operation_id="openapi_json",
)
async def openapi_json():
    """
    Returns the OpenAPI JSON for the backend API.
    """
    try:
        return app.openapi()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# TIMELAPSE
@app.post("/timelapse/start", response_model=TimelapseStatus)
async def start_timelapse(config: TimelapseConfig) -> TimelapseStatus:
    return await camera_service.start_timelapse(config)

@app.post("/timelapse/stop", response_model=TimelapseStatus)
async def stop_timelapse() -> TimelapseStatus:
    return await camera_service.stop_timelapse()

@app.get("/timelapse/status", response_model=TimelapseStatus)
async def timelapse_status() -> TimelapseStatus:
    return await camera_service.get_timelapse_status()

@app.get("/timelapse/frame-info", response_model=TimelapseStatus)
async def timelapse_frame_info() -> TimelapseStatus:
    return await camera_service.get_timelapse_frame_info()

@app.get(
    "/timelapse/latest-frame",
    responses={httpx.codes.OK: {"mediaType": "image/jpeg"}},
    response_class=Response
)
async def get_latest_frame() -> Response:
    image_bytes = await camera_service.get_latest_timelapse_frame()
    return Response(content=image_bytes, media_type="image/jpeg")

@app.get("/timelapse", response_model=list[TimelapseMetadata])
async def list_timelapses_endpoint() -> list[TimelapseMetadata]:
    return await camera_service.list_timelapses()

@app.get(
    "/timelapse/{timelapse_id}/download",
    responses={httpx.codes.OK: {"mediaType": "video/mp4"}},
    response_class=Response
)
async def download_timelapse(timelapse_id: str) -> Response:
    video_bytes = await camera_service.download_timelapse(timelapse_id)
    return Response(
        content=video_bytes,
        media_type="video/mp4",
        headers={"Content-Disposition": f"attachment; filename=timelapse_{timelapse_id}.mp4"}
    )

@app.delete("/timelapse/{timelapse_id}", status_code=httpx.codes.NO_CONTENT)
async def delete_timelapse(timelapse_id: str) -> None:
    await camera_service.delete_timelapse(timelapse_id)