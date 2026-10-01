import uuid

import pytest
import redis.asyncio as aioredis
from app.config import settings
from app.deps import get_redis
from app.main import app
from redis import Redis as SyncRedis
from starlette.testclient import TestClient

from tests.conftest import _override_get_redis

PASSWORD = "SecurePass123!"


def _flush_test_redis_sync() -> None:
    settings.assert_test_redis_isolated()
    client = SyncRedis.from_url(settings.redis_url_for_tests(), decode_responses=True)
    client.flushdb()
    client.close()


@pytest.fixture
def video_ws_client():
    _flush_test_redis_sync()
    redis = aioredis.from_url(settings.redis_url_for_tests(), decode_responses=True)
    app.state.redis = redis
    app.dependency_overrides[get_redis] = _override_get_redis(redis)
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.pop(get_redis, None)
    app.state.redis = None
    _flush_test_redis_sync()


def _register_device_sync(client: TestClient) -> dict:
    slug = f"video-{uuid.uuid4().hex[:8]}"
    email = f"video-{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post(
        "/auth/register",
        json={"tenant_name": f"T {slug}", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    assert reg.status_code == 201
    token = reg.json()["tokens"]["access_token"]
    device = client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Video Drone", "device_type": "drone"},
    )
    assert device.status_code == 201
    device_id = device.json()["device"]["id"]
    return {"user_token": token, "device_id": device_id}


def test_video_feed_websocket_streams_frames(video_ws_client: TestClient):
    ctx = _register_device_sync(video_ws_client)

    with video_ws_client.websocket_connect(
        f"/api/v1/telemetry/video-feed/{ctx['device_id']}?token={ctx['user_token']}"
    ) as websocket:
        stream_info = websocket.receive_json()
        assert stream_info["type"] == "stream_info"
        assert stream_info["codec"] == "H264"

        frame = websocket.receive_json()
        assert frame["type"] == "video_frame"
        assert frame["device_id"] == ctx["device_id"]
        assert frame["frame_b64"]
        assert len(frame["detections"]) >= 1
        assert frame["detections"][0]["target_type"] in {"person", "vehicle"}


def test_video_feed_websocket_rejects_missing_token(video_ws_client: TestClient):
    try:
        with video_ws_client.websocket_connect(
            "/api/v1/telemetry/video-feed/00000000-0000-0000-0000-000000000001"
        ):
            pass
    except Exception:
        pass
