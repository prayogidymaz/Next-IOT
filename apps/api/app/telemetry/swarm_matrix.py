"""Build swarm distance matrix from latest device telemetry positions."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.models.device import Device
from app.telemetry.cache import get_latest_telemetry
from app.telemetry.schemas import SwarmLinkItem, SwarmMatrixResponse
from app.telemetry.swarm_distance import SwarmDistanceCalculator, SwarmNode
from app.types.json_types import as_json_object, metric_float
from app.types.redis_client import RedisClient


async def get_swarm_matrix(
    db: AsyncSession,
    redis: RedisClient,
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
        metrics = as_json_object(cached.get("metrics")) or {}
        lat = metric_float(metrics, "latitude", "lat")
        lon = metric_float(metrics, "longitude", "lon")
        if lat is None or lon is None:
            continue
        alt = metric_float(metrics, "altitude_m", "altitude", "alt")
        nodes.append(
            SwarmNode(
                device_id=str(device.id),
                lat=lat,
                lon=lon,
                alt=alt,
            )
        )

    calculator = SwarmDistanceCalculator()
    links = calculator.compute_links(nodes)
    return SwarmMatrixResponse(
        node_count=len(nodes),
        link_count=len(links),
        collision_threshold_m=calculator.collision_threshold_m,
        has_collision_risk=any(link.collision_risk for link in links),
        links=[
            SwarmLinkItem(
                device_a_id=link.device_a_id,
                device_b_id=link.device_b_id,
                distance_m=link.distance_m,
                collision_risk=link.collision_risk,
                warning=link.warning,
            )
            for link in links
        ],
    )
