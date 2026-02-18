from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse

from . import manager
import io

def get_image():
    """
    Retrieves the latest camera image, refreshing it if expired.
    Returns:
        bytes: The PNG-encoded image bytes.
    Raises:
        Exception: If image acquisition or encoding fails.
    """
    try:
        last_image = manager.get_image()
        if not last_image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except OSError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Camera not available."
        )   

    return StreamingResponse(io.BytesIO(last_image[0]), media_type="image/png")