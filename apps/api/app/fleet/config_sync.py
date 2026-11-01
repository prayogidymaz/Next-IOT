"""Push config to devices via MQTT (ack tracking TODO)."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import CurrentUser
from app.types.json_types import JsonObject


async def sync_config_to_group(
    db: AsyncSession,
    user: CurrentUser,
    group_id: uuid.UUID,
    config: JsonObject,
    mqtt_publisher: object | None,
) -> dict[str, int | float]:
    _ = (db, user, group_id, config, mqtt_publisher)
    # TODO: resolve devices from group tag_filter_json, publish to devices/{id}/config
    return {"targeted": 0, "acked": 0, "ack_rate": 0.0}
