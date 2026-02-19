from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from . import service

router = APIRouter(prefix="/picture", tags=["Pictures"])

@router.get("/", 
            response_class=StreamingResponse)
async def picture():
    return service.get_image()