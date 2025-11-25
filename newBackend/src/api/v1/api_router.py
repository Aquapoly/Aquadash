from fastapi import APIRouter

from src.features.prototypes import router as prototypes_router
from src.features.sensors import router as sensors_router
from src.features.actuators import router as actuators_router
from src.features.measurements import router as measurements_router
from src.features.users import router as users_router

api_router = APIRouter()

# Include all the feature routers
api_router.include_router(prototypes_router.router)
api_router.include_router(sensors_router.router)
api_router.include_router(actuators_router.router)
api_router.include_router(measurements_router.router)
api_router.include_router(users_router.router)
