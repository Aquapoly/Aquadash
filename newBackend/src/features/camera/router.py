from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from . import service

router = APIRouter(prefix="/sensors", tags=["Sensors"])

@router.get("/", 
            response_class=StreamingResponse)
async def picture():
    return service.get_image()