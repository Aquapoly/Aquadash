import uuid
import pytest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from .. import timelapse_client as timelapse_module
from ..timelapse_client import TimelapseClient
from ..camera_client import CameraClient
from ..main import timelapse_client as app_timelapse_client


@pytest.fixture
def root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "timelapses"
    root.mkdir()
    monkeypatch.setattr(timelapse_module, "TIMELAPSES_DIR", root)
    return root


@pytest.fixture
def timelapses(root: Path, mock_camera: CameraClient) -> TimelapseClient:
    return TimelapseClient(mock_camera)


def test_folder_valid_id(timelapses: TimelapseClient, root: Path):
    """A plain id should map to a direct child of the timelapses directory."""
    timelapse_id = str(uuid.uuid4())
    assert timelapses._folder(timelapse_id) == root.resolve() / timelapse_id


@pytest.mark.parametrize("timelapse_id", ["..", ".", "../..", "a/b", "../outside"])
def test_folder_rejects_escaping_ids(timelapses: TimelapseClient, timelapse_id: str):
    """Ids that don't resolve to a direct child of the timelapses directory should be rejected."""
    with pytest.raises(FileNotFoundError):
        timelapses._folder(timelapse_id)


def test_folder_rejects_symlink_out(timelapses: TimelapseClient, root: Path, tmp_path: Path):
    """A symlink inside the timelapses directory shouldn't lead outside of it."""
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "link").symlink_to(outside)
    with pytest.raises(FileNotFoundError):
        timelapses._folder("link")


def test_folder_follows_symlinked_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mock_camera: CameraClient):
    """A symlinked timelapses directory should still accept valid ids."""
    real_root = tmp_path / "real"
    real_root.mkdir()
    link_root = tmp_path / "timelapses"
    link_root.symlink_to(real_root)
    monkeypatch.setattr(timelapse_module, "TIMELAPSES_DIR", link_root)
    assert TimelapseClient(mock_camera)._folder("abc") == real_root / "abc"


def test_delete_parent_is_rejected(timelapses: TimelapseClient, root: Path):
    """Deleting '..' should never touch the parent of the timelapses directory."""
    sibling = root.parent / "keep_me"
    sibling.mkdir()
    with pytest.raises(FileNotFoundError):
        timelapses.delete("..")
    assert root.exists() and sibling.exists()


def test_delete_removes_timelapse(timelapses: TimelapseClient, root: Path):
    timelapse_id = str(uuid.uuid4())
    (root / timelapse_id).mkdir()
    timelapses.delete(timelapse_id)
    assert not (root / timelapse_id).exists()


@pytest.mark.parametrize("method, path", [
    ("DELETE", "/timelapse/not-a-uuid"),
    ("DELETE", "/timelapse/%2E%2E"),
    ("GET", "/timelapse/not-a-uuid/download"),
    ("GET", "/timelapse/%2E%2E/download"),
])
def test_routes_reject_non_uuid_ids(client: TestClient, method: str, path: str):
    """Non-UUID ids should be rejected before reaching the timelapse client."""
    with patch.object(app_timelapse_client, "delete") as delete, \
         patch.object(app_timelapse_client, "download") as download:
        response = client.request(method, path)
    assert response.status_code == 422
    delete.assert_not_called()
    download.assert_not_called()


def test_delete_route_passes_uuid_as_str(client: TestClient):
    timelapse_id = uuid.uuid4()
    with patch.object(app_timelapse_client, "delete", return_value=None) as delete:
        response = client.delete(f"/timelapse/{timelapse_id}")
    assert response.status_code == 200
    delete.assert_called_once_with(str(timelapse_id))
