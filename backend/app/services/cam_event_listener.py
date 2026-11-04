import asyncio
import logging
from urllib.parse import urlsplit, urlunsplit

import websockets
from pydantic import ValidationError

from . import cam_client as camera_service
from ..ws_manager import manager as ws_manager
from shared.timelapse_models import TimelapseStatus

logger = logging.getLogger(__name__)
RECONNECT_DELAY_SECONDS = 3


def _event_websocket_url() -> str:
    parts = urlsplit(camera_service.CAM_CLIENT_BASE_URL)
    scheme = {"http": "ws", "https": "wss"}[parts.scheme]
    return urlunsplit((scheme, parts.netloc, "/ws/timelapse-events", "", ""))


async def listen_for_timelapse_events() -> None:
    url = _event_websocket_url()
    while True:
        try:
            async with websockets.connect(url) as connection:
                logger.info("Connected to cam-client timelapse event stream")
                async for message in connection:
                    try:
                        event = TimelapseStatus.model_validate_json(message)
                    except ValidationError as exc:
                        logger.warning("Ignoring invalid timelapse event from cam-client: %s", exc)
                        continue
                    await ws_manager.broadcast(event.model_dump(mode="json"))
        except (OSError, websockets.exceptions.WebSocketException) as exc:
            logger.warning(
                "cam-client timelapse event stream disconnected; retrying in %s seconds: %s",
                RECONNECT_DELAY_SECONDS,
                exc,
            )
        await asyncio.sleep(RECONNECT_DELAY_SECONDS)
