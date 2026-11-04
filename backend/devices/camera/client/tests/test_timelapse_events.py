from datetime import datetime, timedelta, timezone
import queue
from unittest.mock import patch

from fastapi.testclient import TestClient

from shared.timelapse_models import TimelapseConfig, TimelapseMetadata, TimelapseStatus
from ..main import app, timelapse_client


def test_timelapse_events_websocket_sends_initial_state_and_updates():
    initial_status = TimelapseStatus(isRecording=False, metadata=None)
    now = datetime.now(timezone.utc)
    metadata = TimelapseMetadata(
        id="timelapse-id",
        name="Test timelapse",
        frames=1,
        framerate=24,
        start_date=now,
        latest_frame_date=now,
        end_date=now + timedelta(seconds=60),
        ready=False,
    )
    updated_status = TimelapseStatus(
        isRecording=True,
        metadata=metadata,
        config=TimelapseConfig(frequency=1, duration=60, framerate=24),
    )

    event_pending = True

    def wait_for_event(timeout):
        nonlocal event_pending
        if event_pending:
            event_pending = False
            return updated_status.model_dump_json()
        raise queue.Empty

    with (
        patch.object(timelapse_client, "status", return_value=initial_status),
        patch.object(
            timelapse_client,
            "wait_for_status_event",
            side_effect=wait_for_event,
        ) as wait_for_status_event,
    ):
        with TestClient(app) as client:
            with client.websocket_connect("/ws/timelapse-events") as websocket:
                assert TimelapseStatus.model_validate_json(websocket.receive_text()) == initial_status
                assert TimelapseStatus.model_validate_json(websocket.receive_text()) == updated_status

    wait_for_status_event.assert_any_call(1.0)
