from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse

from shared.timelapse_models import TimelapseMetadata
from camera_client import CameraClient, CameraSocketNotFoundError, CameraNotAvailableError, CAMERA_NAME
from timelapse_client import TimelapseClient, TimelapseConfig, TimelapseStatus

app = FastAPI()

camera_client = CameraClient(CAMERA_NAME)
timelapse_client = TimelapseClient(camera_client)


# --- Camera ---

@app.get("/picture")
def picture():
    try:
        image_bytes: bytes = camera_client.get_image()
        return Response(content=image_bytes, media_type="image/png")
    except PermissionError as e:
        print(f"[Error] /picture permission error: {e}")
        return Response(content="Camera service unavailable.", status_code=503)
    except CameraSocketNotFoundError as e:
        print(f"[Error] /picture camera socket not found: {e}")
        return Response(content="Camera service unavailable.", status_code=503)
    except CameraNotAvailableError as e:
        return Response(content=str(e), status_code=404)

@app.get("/health")
def health():
    return {"status": "healthy"}


# --- Timelapse ---

@app.post("/timelapse/start")
def start_timelapse(config: TimelapseConfig) -> TimelapseStatus:
    try:
        return timelapse_client.start(config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/timelapse/stop")
def stop_timelapse() -> TimelapseStatus:
    try:
        return timelapse_client.stop()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/timelapse/status")
def timelapse_status() -> TimelapseStatus:
    return timelapse_client.status()

@app.get("/timelapse/latest-frame")
def get_latest_frame():
    try:
        latest_frame_path = timelapse_client.get_latest_frame()
        return FileResponse(latest_frame_path, media_type="image/jpeg", filename="timelapse_{timelapse_id}_latest.jpeg")
        return FileResponse(timelapse_client.get_latest_frame())
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/timelapse")
def list_timelapses() -> list[TimelapseMetadata]:
    return timelapse_client.list()

@app.get("/timelapse/{timelapse_id}/download")
def download_timelapse(timelapse_id: str):
    try:
        video_path = timelapse_client.download(timelapse_id)
        return FileResponse(
            video_path,
            media_type="video/mp4",
            filename=f"timelapse_{timelapse_id}.mp4"
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/timelapse/{timelapse_id}")
def delete_timelapse(timelapse_id: str) -> None:
    try:
        return timelapse_client.delete(timelapse_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))