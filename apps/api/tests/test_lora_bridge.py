import json
from unittest.mock import AsyncMock, patch

import pytest
import redis.asyncio as aioredis

from app.config import settings
from app.hardware.events import GATEWAY_STATUS_KEY, LORA_TELEMETRY_CHANNEL
from app.hardware.lora_bridge import LoRaBridge
from app.hardware.parser import LoRaPacket


@pytest.fixture
def sample_packet() -> LoRaPacket:
    return LoRaPacket(
        node_id="DRONE-01",
        latitude=3.595,
        longitude=98.665,
        altitude_m=60.0,
        rssi=-85.0,
        snr=9.5,
        raw='{"node_id":"DRONE-01","lat":3.595,"lon":98.665,"alt":60,"rssi":-85,"snr":9.5}',
    )


@pytest.fixture
async def redis_client():
    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    yield redis
    await redis.delete(GATEWAY_STATUS_KEY)
    await redis.aclose()


@pytest.mark.asyncio
async def test_process_packet_publishes_redis_and_gateway_status(redis_client, sample_packet):
    bridge = LoRaBridge(redis_client, api_base_url="http://test")
    device_ctx = {
        "device_id": "00000000-0000-0000-0000-000000000001",
        "client_id": "dev_test",
        "client_secret": "secret_test",
    }

    pubsub = redis_client.pubsub()
    await pubsub.subscribe(LORA_TELEMETRY_CHANNEL)
    for _ in range(50):
        sub_msg = await pubsub.get_message(ignore_subscribe_messages=False, timeout=0.1)
        if sub_msg and sub_msg.get("type") == "subscribe":
            break

    with patch.object(bridge, "_resolve_device", AsyncMock(return_value=device_ctx)), patch.object(
        bridge, "_ensure_device_online", AsyncMock()
    ), patch.object(bridge, "_forward_to_api", AsyncMock()) as forward_mock:
        await bridge.process_packet(sample_packet)

    forward_mock.assert_awaited_once()
    status_raw = await redis_client.get(GATEWAY_STATUS_KEY)
    assert status_raw is not None
    status = json.loads(status_raw)
    assert status["node_id"] == "DRONE-01"
    assert status["rssi"] == -85.0
    assert status["packets_received"] == 1

    message = None
    for _ in range(20):
        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.25)
        if message is not None:
            break
    assert message is not None
    payload = json.loads(message["data"])
    assert payload["node_id"] == "DRONE-01"
    assert payload["latitude"] == 3.595

    await pubsub.unsubscribe(LORA_TELEMETRY_CHANNEL)
    await pubsub.aclose()


@pytest.mark.asyncio
async def test_gateway_status_endpoint(client, redis_client, unique_slug, unique_email):
    await redis_client.set(
        GATEWAY_STATUS_KEY,
        json.dumps(
            {
                "serial_connected": True,
                "serial_port": settings.lora_bridge_serial_port,
                "lora_link": "connected",
                "rssi": -72.0,
                "snr": 10.5,
                "packets_received": 12,
            }
        ),
    )

    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": "HW Tenant",
            "tenant_slug": unique_slug,
            "email": unique_email,
            "password": "SecurePass123!",
        },
    )
    assert reg.status_code == 201
    token = reg.json()["tokens"]["access_token"]
    resp = await client.get(
        "/api/v1/hardware/gateway-status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["serial_connected"] is True
    assert body["rssi"] == -72.0
    assert body["packets_received"] == 12
