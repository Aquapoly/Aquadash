import asyncio
import queue
from contextlib import suppress
from uuid import UUID

from fastapi import FastAPI, HTTPException, Response
from fastapi import WebSocket, WebSocketDisconnect
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


@app.websocket("/ws/timelapse-events")
async def timelapse_events(websocket: WebSocket):
    await websocket.accept()
    try:
        await websocket.send_text(timelapse_client.status().model_dump_json())

        async def send_events():
            while True:
                try:
                    event = await asyncio.to_thread(timelapse_client.wait_for_status_event, 1.0)
                except queue.Empty:
                    continue
                await websocket.send_text(event)

        async def wait_for_disconnect():
            try:
                while True:
                    await websocket.receive_text()
            except WebSocketDisconnect:
                return

        sender = asyncio.create_task(send_events())
        receiver = asyncio.create_task(wait_for_disconnect())
        done, pending = await asyncio.wait(
            {sender, receiver},
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
        for task in done:
            with suppress(WebSocketDisconnect):
                task.result()
    except WebSocketDisconnect:
        return


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
        timelapse_id = latest_frame_path.parent.name
        return FileResponse(latest_frame_path, media_type="image/jpeg", filename=f"timelapse_{timelapse_id}_latest.jpeg")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/timelapse/{timelapse_id}/preview")
def get_timelapse_preview(timelapse_id: UUID):
    try:
        preview_path = timelapse_client.get_preview(str(timelapse_id))
        return FileResponse(preview_path, media_type="image/jpeg")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/timelapse")
def list_timelapses() -> list[TimelapseMetadata]:
    return timelapse_client.list()

@app.get("/timelapse/{timelapse_id}/download")
def download_timelapse(timelapse_id: UUID):
    try:
        video_path = timelapse_client.download(str(timelapse_id))
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
def delete_timelapse(timelapse_id: UUID) -> None:
    try:
        return timelapse_client.delete(str(timelapse_id))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))