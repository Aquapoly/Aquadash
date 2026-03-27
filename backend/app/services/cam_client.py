import httpx
from fastapi import HTTPException, status

CAM_CLIENT_BASE_URL: str = "http://cam-client:9000"
PICTURE: str = "/picture"
TIMELAPSE: str = "/timelapse"

_client: httpx.AsyncClient | None = None
TIMEOUT_SECONDS: float = 5.0

async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=TIMEOUT_SECONDS)
    return _client

def _unavailable(detail: str = "Camera service unavailable."):
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


def _not_found(detail: str = "Not found."):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


async def _get(path: str, timeout: float | None = None) -> httpx.Response:
    try:
        client = await get_client()
        url = f"{CAM_CLIENT_BASE_URL}{path}"
        if timeout is None:
            response = await client.get(url)
        else:
            response = await client.get(url, timeout=timeout)
        return response
    except (httpx.RequestError, httpx.ConnectError):
        _unavailable()


async def _post(path: str, json: dict = None) -> httpx.Response:
    try:
        client = await get_client()
        url = f"{CAM_CLIENT_BASE_URL}{path}"
        response = await client.post(url, json=json)
        return response
    except (httpx.RequestError, httpx.ConnectError):
        _unavailable()


async def _delete(path: str) -> httpx.Response:
    try:
        client = await get_client()
        url = f"{CAM_CLIENT_BASE_URL}{path}"
        response = await client.delete(url)
        return response
    except (httpx.RequestError, httpx.ConnectError):
        _unavailable()


async def get_picture() -> bytes:
    response = await _get(PICTURE)
    if not response.is_success:
        _not_found("Camera unavailable.")
    return response.content


async def start_timelapse(config: dict) -> dict:
    response = await _post(f"{TIMELAPSE}/start", json=config)
    if response.status_code == 400:
        raise HTTPException(status_code=400, detail=response.json().get("detail"))
    if not response.is_success:
        _unavailable()
    return response.json()


async def stop_timelapse() -> dict:
    response = await _post(f"{TIMELAPSE}/stop")
    if response.status_code == 400:
        raise HTTPException(status_code=400, detail=response.json().get("detail"))
    if not response.is_success:
        _unavailable()
    return response.json()


async def get_timelapse_status() -> dict:
    response = await _get(f"{TIMELAPSE}/status")
    if not response.is_success:
        _unavailable()
    return response.json()


async def get_latest_timelapse_frame() -> bytes:
    response = await _get(f"{TIMELAPSE}/latest-frame")
    if response.status_code == 404:
        _not_found("No frame available.")
    if not response.is_success:
        _unavailable()
    return response.content


async def list_timelapses() -> dict:
    response = await _get(f"{TIMELAPSE}")
    if not response.is_success:
        _unavailable()
    return response.json()


async def download_timelapse(timelapse_id: str) -> bytes:
    response = await _get(f"{TIMELAPSE}/{timelapse_id}/download", timeout=30.0)
    if response.status_code == 404:
        _not_found(f"Timelapse {timelapse_id} not found.")
    if response.status_code == 500:
        raise HTTPException(status_code=500, detail=response.json().get("detail"))
    if not response.is_success:
        _unavailable()
    return response.content


async def delete_timelapse(timelapse_id: str) -> dict:
    response = await _delete(f"{TIMELAPSE}/{timelapse_id}")
    if response.status_code == 404:
        _not_found(f"Timelapse {timelapse_id} not found.")
    if not response.is_success:
        _unavailable()
    return response.json()

async def get_timelapse_frame_info() -> dict:
    response = await _get("/timelapse/status")
    if not response.is_success:
        _unavailable()
    data = response.json()
    return {
        "frames_taken": data["frames_taken"],
        "latest_frame_time": data["latest_frame_time"],
    }


async def close_client() -> None:
    """Close the shared AsyncClient instance if it exists."""
    global _client
    if _client is not None:
        try:
            await _client.aclose()
        finally:
            _client = None