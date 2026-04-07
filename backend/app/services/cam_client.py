import httpx
from fastapi import HTTPException, status

from shared.timelapse_models import TimelapseMetadata, TimelapseConfig, TimelapseStatus

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
    except (httpx.RequestError, httpx.ConnectError) as e:
        print(f"[Error] cam-client {path} request failed: {e}")
        _unavailable()


async def get_picture() -> bytes:
    response = await _get(PICTURE)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        _not_found("Camera unavailable.")
    if response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        if response.text:
            print(f"[Error] cam-client /picture returned 503: {response.text}")
        _unavailable("Camera service unavailable.")
    if not response.is_success:
        if response.text:
            print(f"[Error] cam-client /picture returned {response.status_code}: {response.text}")
        _unavailable("Camera service unavailable.")
    return response.content


async def start_timelapse(config: TimelapseConfig) -> TimelapseStatus:
    response = await _post(f"{TIMELAPSE}/start", json=config.model_dump())
    if response.status_code == 400:
        if response.text:
            print(f"[Error] cam-client /timelapse/start returned 400: {response.text}")
        raise HTTPException(status_code=400, detail="Invalid request")
    if not response.is_success:
        _unavailable()
    return TimelapseStatus.model_validate(response.json())


async def stop_timelapse() -> TimelapseStatus:
    response = await _post(f"{TIMELAPSE}/stop")
    if response.status_code == 400:
        raise HTTPException(status_code=400, detail=response.json().get("detail"))
    if not response.is_success:
        _unavailable()
    return TimelapseStatus.model_validate(response.json())


async def get_timelapse_status() -> TimelapseStatus:
    response = await _get(f"{TIMELAPSE}/status")
    if not response.is_success:
        _unavailable()
    return TimelapseStatus.model_validate(response.json())


async def get_latest_timelapse_frame() -> bytes:
    response = await _get(f"{TIMELAPSE}/latest-frame")
    if response.status_code == 404:
        _not_found("No frame available.")
    if not response.is_success:
        _unavailable()
    return response.content


async def list_timelapses() -> list[TimelapseMetadata]:
    response = await _get(TIMELAPSE)
    if not response.is_success:
        _unavailable()
    return [TimelapseMetadata.model_validate(item) for item in response.json()]

async def download_timelapse(timelapse_id: str) -> bytes:
    response = await _get(f"{TIMELAPSE}/{timelapse_id}/download", timeout=30.0)
    if response.status_code == 404:
        _not_found(f"Timelapse {timelapse_id} not found.")
    if response.status_code == 500:
        raise HTTPException(status_code=500, detail=response.json().get("detail"))
    if not response.is_success:
        _unavailable()
    return response.content


async def delete_timelapse(timelapse_id: str) -> None:
    response: httpx.Response = await _delete(f"{TIMELAPSE}/{timelapse_id}")
    if response.status_code == 404:
        _not_found(f"Timelapse {timelapse_id} not found.")
    if not response.is_success:
        _unavailable()
    return

async def get_timelapse_frame_info() -> TimelapseStatus:
    response = await _get("/timelapse/status")
    if not response.is_success:
        _unavailable()
    return TimelapseStatus.model_validate(response.json())


async def close_client() -> None:
    """Close the shared AsyncClient instance if it exists."""
    global _client
    if _client is not None:
        try:
            await _client.aclose()
        finally:
            _client = None