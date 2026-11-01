"""Redis-backed webhook retry with exponential backoff."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import select

from app.database import async_session
from app.types.json_types import JsonObject
from app.types.redis_client import RedisClient
from app.webhooks.models import Webhook, WebhookDelivery
from app.webhooks.service import deliver_event

logger = logging.getLogger(__name__)

QUEUE_KEY = "webhooks:retry"
BACKOFF_SECONDS = (5, 30, 120, 600, 3600)


async def enqueue_failed_delivery(redis: RedisClient, delivery_id: uuid.UUID, attempt: int) -> None:
    delay = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
    payload = json.dumps({"delivery_id": str(delivery_id), "attempt": attempt, "run_at": datetime.now(tz=UTC).timestamp() + delay})
    await redis.rpush(QUEUE_KEY, payload)


async def retry_worker_loop(redis: RedisClient, stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        raw = await redis.lpop(QUEUE_KEY)
        if raw is None:
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                continue
            continue
        try:
            item = json.loads(raw)
            delivery_id = uuid.UUID(str(item["delivery_id"]))
            attempt = int(item.get("attempt", 0))
        except (ValueError, KeyError, json.JSONDecodeError):
            continue
        async with async_session() as db:
            delivery = await db.get(WebhookDelivery, delivery_id)
            if delivery is None or delivery.status == "delivered":
                continue
            hook = await db.get(Webhook, delivery.webhook_id)
            if hook is None:
                delivery.status = "dead_letter"
                await db.commit()
                continue
            ok = await deliver_event(db, hook, delivery.event_type, {})
            if ok:
                delivery.status = "delivered"
                delivery.delivered_at = datetime.now(tz=UTC)
            else:
                delivery.retry_count += 1
                delivery.last_error = "delivery failed"
                if delivery.retry_count >= 5:
                    delivery.status = "dead_letter"
                else:
                    delivery.status = "pending"
                    await enqueue_failed_delivery(redis, delivery.id, delivery.retry_count)
            await db.commit()


async def list_deliveries(db: object, webhook_id: uuid.UUID) -> list[WebhookDelivery]:
    from sqlalchemy.ext.asyncio import AsyncSession

    if not isinstance(db, AsyncSession):
        return []
    rows = await db.scalars(select(WebhookDelivery).where(WebhookDelivery.webhook_id == webhook_id).order_by(WebhookDelivery.created_at.desc()))
    return list(rows.all())
