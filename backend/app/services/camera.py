import httpx
from fastapi import HTTPException, status

CAM_CLIENT_URL: str = "http://cam-client:9000/picture"

def _raise_not_found():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera unavailable.")

async def get_picture() -> bytes:
    """
    Fetches the latest camera image from the camera client service.

    Status codes:
        200: Successfully retrieved the image.
        404: Camera is unavailable or there was an error fetching the image.
    """
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response: httpx.Response = await client.get(CAM_CLIENT_URL)

        if not response.is_success:
            _raise_not_found()

        return response.content

    except (httpx.RequestError, httpx.ConnectError):
        # From end user POV, this is the same as the camera being unavailable
        _raise_not_found()