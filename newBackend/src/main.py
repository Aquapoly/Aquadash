from fastapi import FastAPI
from src.api.v1.api_router import api_router

app = FastAPI(title="Aquadash API")

@app.get("/", tags=["Health Check"])
def health_check():
    """
    Health check endpoint to ensure the API is running.
    """
    return {"status": "ok", "message": "Aquadash API is running."}

# Include the main API router with a prefix
app.include_router(api_router, prefix="/api/v1")








from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
# from fastapi_utils.openapi import simplify_operation_ids
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import datetime, timedelta
import io
# from jose import JWTError, jwt


from . import crud, models, schemas
from .database import engine, get_db
from .classes.sensor_type import SensorType
from .services import camera
from .services.actuator import get_actuator_activation
from .security import authentification
from .security import permissions

models.Base.metadata.create_all(bind=engine)


sensors_data = dict()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = next(get_db())  
    crud.default_populate_database(db)  
    yield


app = FastAPI(lifespan=lifespan)

origins = ["http://localhost", "http://localhost:4200", "http://127.0.0.1:4200", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
