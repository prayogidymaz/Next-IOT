"""Automation pipeline event bus via Redis pub/sub."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import redis.asyncio as aioredis
from pydantic import JsonValue

AUTOMATION_EVENTS_CHANNEL = "automation:events"
AUTOMATION_PIPELINES_CHANNEL = "automation:pipelines:updated"


async def publish_automation_event(
    redis: aioredis.Redis,
    *,
    tenant_id: str,
    event_type: str,
    context: dict[str, JsonValue],
) -> None:
    payload = {
        "tenant_id": tenant_id,
        "event_type": event_type,
        "context": context,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    await redis.publish(AUTOMATION_EVENTS_CHANNEL, json.dumps(payload, default=str))


async def publish_pipeline_rules_updated(
    redis: aioredis.Redis,
    *,
    tenant_id: str,
    pipeline_id: str,
    action: str,
    pipeline: dict[str, JsonValue],
) -> None:
    payload = {
        "event": "pipeline.rules.updated",
        "action": action,
        "tenant_id": tenant_id,
        "pipeline_id": pipeline_id,
        "pipeline": {
            "name": pipeline.get("name"),
            "description": pipeline.get("description"),
            "is_active": pipeline.get("is_active", True),
            "nodes_json": pipeline.get("nodes_json") or [],
            "edges_json": pipeline.get("edges_json") or [],
        },
        "timestamp": datetime.now(UTC).isoformat(),
    }
    await redis.publish(AUTOMATION_PIPELINES_CHANNEL, json.dumps(payload, default=str))
