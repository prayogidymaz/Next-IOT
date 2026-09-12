"""Build swarm distance matrix from latest device telemetry positions."""

from __future__ import annotations

import uuid

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.models.device import Device
from app.telemetry.cache import get_latest_telemetry
from app.telemetry.flight_replay import _metric_float
from app.telemetry.schemas import SwarmLinkItem, SwarmMatrixResponse
from app.telemetry.swarm_distance import SwarmDistanceCalculator, SwarmNode


async def get_swarm_matrix(
    db: AsyncSession,
    redis: aioredis.Redis,
    user: CurrentUser,
) -> SwarmMatrixResponse:
    query = select(Device)
    if not user.is_super_admin:
        query = query.where(Device.tenant_id == user.tenant_id)

    devices = (await db.scalars(query)).all()
    nodes: list[SwarmNode] = []

    for device in devices:
        cached = await get_latest_telemetry(redis, str(device.id))
        if cached is None:
            continue
        metrics = cached.get("metrics") or {}
        lat = _metric_float(metrics, "latitude", "lat")
        lon = _metric_float(metrics, "longitude", "lon")
        if lat is None or lon is None:
            continue
        alt = _metric_float(metrics, "altitude_m", "altitude", "alt")
        nodes.append(
            SwarmNode(
                device_id=str(device.id),
                lat=lat,
                lon=lon,
                alt=alt,
            )
        )

    calculator = SwarmDistanceCalculator()
    matrix = calculator.compute_matrix(nodes)
    return SwarmMatrixResponse(
        node_count=matrix["node_count"],
        link_count=matrix["link_count"],
        collision_threshold_m=matrix["collision_threshold_m"],
        has_collision_risk=matrix["has_collision_risk"],
        links=[SwarmLinkItem.model_validate(link) for link in matrix["links"]],
    )
