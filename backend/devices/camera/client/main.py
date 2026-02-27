from fastapi import FastAPI, Response
from camera_client import camera_client, CameraSocketNotFoundError, CameraNotAvailableError

app = FastAPI()

@app.get("/picture")
def picture():
    try:
        image_bytes: bytes = camera_client.get_image()
        return Response(content=image_bytes, media_type="image/png")
    except PermissionError as e:
        return Response(content=str(e), status_code=503)
    except CameraSocketNotFoundError as e:
        return Response(content=str(e), status_code=503)
    except CameraNotAvailableError as e:
        return Response(content=str(e), status_code=404)

@app.get("/health")
def health():
    return {"status": "healthy"}