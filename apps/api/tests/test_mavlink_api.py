import base64

import pytest
from httpx import AsyncClient
from pymavlink.dialects.v20 import common as mavlink

from app.mavlink.bridge_service import MavlinkBridgeService
from tests.test_commands import PASSWORD, _register_and_create_device


def _heartbeat_b64() -> str:
    bridge = MavlinkBridgeService()
    mav = bridge._mav  # noqa: SLF001
    msg = mav.heartbeat_encode(
        mavlink.MAV_TYPE_QUADROTOR,
        mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
        mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        0,
        mavlink.MAV_STATE_ACTIVE,
    )
    return base64.b64encode(msg.pack(mav)).decode("ascii")


@pytest.mark.asyncio
async def test_mavlink_decode_endpoint(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)

    resp = await client.post(
        "/api/v1/hardware/mavlink/decode",
        headers={"Authorization": f"Bearer {ctx['token']}"},
        json={"data_b64": _heartbeat_b64(), "device_id": ctx["device_id"]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "HEARTBEAT" in body["messages"]
    assert body["snapshot"]["mavlink_connected"] is True


@pytest.mark.asyncio
async def test_mavlink_encode_rtl(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)

    resp = await client.post(
        "/api/v1/hardware/mavlink/encode",
        headers={"Authorization": f"Bearer {ctx['token']}"},
        json={"command": "RTL"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["command"] == "RTL"
    assert body["byte_length"] > 0
    assert base64.b64decode(body["data_b64"])[0] == 0xFD


@pytest.mark.asyncio
async def test_mavlink_status_after_decode(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)
    await client.post(
        "/api/v1/hardware/mavlink/decode",
        headers={"Authorization": f"Bearer {ctx['token']}"},
        json={"data_b64": _heartbeat_b64(), "device_id": ctx["device_id"]},
    )

    status = await client.get(
        "/api/v1/hardware/mavlink/status",
        headers={"Authorization": f"Bearer {ctx['token']}"},
        params={"device_id": ctx["device_id"]},
    )
    assert status.status_code == 200
    assert status.json()["connected"] is True
    assert status.json()["protocol_version"] == "2.0"
