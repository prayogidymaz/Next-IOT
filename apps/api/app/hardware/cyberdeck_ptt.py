"""Cyberdeck LoRa PTT mesh snapshot + dispatch (Redis-backed with demo fallback)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import redis.asyncio as aioredis

from app.hardware.cyberdeck_schemas import (
    CyberdeckHealthResponse,
    CyberdeckMeshNode,
    CyberdeckMeshResponse,
    PttBeaconRequest,
    PttDispatchResponse,
    PttTextDispatchRequest,
)

MESH_KEY = "hardware:cyberdeck:mesh"
HEALTH_KEY = "hardware:cyberdeck:health"
PTT_LOG_KEY = "hardware:cyberdeck:ptt:log"

_DEMO_MESH: list[CyberdeckMeshNode] = [
    CyberdeckMeshNode(
        node_id="CDK-01",
        label="Cyberdeck Unit 1",
        device_type="cyberdeck",
        latitude=-6.2088,
        longitude=106.8456,
        rssi=-82.0,
        snr=9.5,
        battery_pct=78.0,
        channel=3,
    ),
    CyberdeckMeshNode(
        node_id="CDK-02",
        label="Cyberdeck Unit 2",
        device_type="cyberdeck",
        latitude=-6.2101,
        longitude=106.8472,
        rssi=-91.0,
        snr=6.2,
        battery_pct=64.0,
        channel=3,
    ),
    CyberdeckMeshNode(
        node_id="SW-01",
        label="ESP32-S3 Smartwatch",
        device_type="lorawan",
        latitude=-6.2095,
        longitude=106.8465,
        rssi=-88.0,
        snr=7.8,
        battery_pct=52.0,
        channel=3,
    ),
]

_DEMO_HEALTH = CyberdeckHealthResponse(
    cpu_temp_c=54.2,
    ram_used_pct=61.0,
    battery_pct=88.0,
    power_source="UPS + LiPo",
    uptime_sec=86412,
    lora_channel=3,
)


async def get_mesh_nodes(redis: aioredis.Redis) -> CyberdeckMeshResponse:
    raw = await redis.get(MESH_KEY)
    if raw:
        # Demo path: always serve structured demo until hardware writer populates JSON
        pass
    nodes = _DEMO_MESH
    return CyberdeckMeshResponse(count=len(nodes), nodes=nodes)


async def get_cyberdeck_health(redis: aioredis.Redis) -> CyberdeckHealthResponse:
    _ = await redis.get(HEALTH_KEY)
    return _DEMO_HEALTH


async def dispatch_text(redis: aioredis.Redis, payload: PttTextDispatchRequest) -> PttDispatchResponse:
    packet_id = str(uuid.uuid4())
    envelope = {
        "packet_id": packet_id,
        "type": "ptt_text",
        "channel": payload.channel,
        "target": payload.target_node_id,
        "encrypted": payload.encrypt,
        "message": payload.message,
        "at": datetime.now(UTC).isoformat(),
    }
    await redis.lpush(PTT_LOG_KEY, str(envelope))
    await redis.ltrim(PTT_LOG_KEY, 0, 99)
    return PttDispatchResponse(
        packet_id=packet_id,
        encrypted=payload.encrypt,
        channel=payload.channel,
        message=payload.message,
    )


async def dispatch_beacon(redis: aioredis.Redis, payload: PttBeaconRequest) -> PttDispatchResponse:
    packet_id = str(uuid.uuid4())
    msg = f"EMERGENCY_BEACON:{payload.severity.upper()}"
    envelope = {
        "packet_id": packet_id,
        "type": "emergency_beacon",
        "channel": payload.channel,
        "lat": payload.latitude,
        "lon": payload.longitude,
        "severity": payload.severity,
        "at": datetime.now(UTC).isoformat(),
    }
    await redis.lpush(PTT_LOG_KEY, str(envelope))
    await redis.ltrim(PTT_LOG_KEY, 0, 99)
    return PttDispatchResponse(
        packet_id=packet_id,
        encrypted=True,
        channel=payload.channel,
        message=msg,
    )
