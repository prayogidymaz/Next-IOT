"""Webhook delivery and CRUD."""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import uuid
from datetime import UTC, datetime

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import CurrentUser
from app.types.json_types import JsonObject
from app.webhooks.models import Webhook
from app.webhooks.schemas import WebhookCreate, WebhookUpdate


def _sign_body(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


async def list_webhooks(db: AsyncSession, user: CurrentUser) -> list[Webhook]:
    rows = await db.scalars(select(Webhook).where(Webhook.tenant_id == user.tenant_id).order_by(Webhook.created_at.desc()))
    return list(rows.all())


async def create_webhook(db: AsyncSession, user: CurrentUser, payload: WebhookCreate) -> Webhook:
    row = Webhook(
        tenant_id=user.tenant_id,
        url=str(payload.url),
        event_types_json=payload.event_types,
        secret_token=payload.secret_token or secrets.token_urlsafe(24),
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def update_webhook(db: AsyncSession, user: CurrentUser, webhook_id: uuid.UUID, payload: WebhookUpdate) -> Webhook:
    row = await db.get(Webhook, webhook_id)
    if row is None or row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    if payload.url is not None:
        row.url = str(payload.url)
    if payload.event_types is not None:
        row.event_types_json = payload.event_types
    if payload.active is not None:
        row.active = payload.active
    await db.commit()
    await db.refresh(row)
    return row


async def delete_webhook(db: AsyncSession, user: CurrentUser, webhook_id: uuid.UUID) -> None:
    row = await db.get(Webhook, webhook_id)
    if row is None or row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    await db.delete(row)
    await db.commit()


async def deliver_event(db: AsyncSession, webhook: Webhook, event_type: str, data: JsonObject) -> bool:
    if not webhook.active:
        return False
    types = webhook.event_types_json if isinstance(webhook.event_types_json, list) else []
    if types and event_type not in [str(t) for t in types]:
        return False
    envelope = {"event": event_type, "data": data}
    body = json.dumps(envelope).encode("utf-8")
    signature = _sign_body(webhook.secret_token, body)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                webhook.url,
                content=body,
                headers={"Content-Type": "application/json", "X-Next-IOT-Signature": signature},
            )
        ok = resp.status_code < 400
    except httpx.HTTPError:
        ok = False
    if ok:
        webhook.last_delivery_at = datetime.now(tz=UTC)
        await db.commit()
    return ok


async def send_test(db: AsyncSession, user: CurrentUser, webhook_id: uuid.UUID) -> dict[str, bool]:
    row = await db.get(Webhook, webhook_id)
    if row is None or row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    ok = await deliver_event(db, row, "webhook.test", {"tenant_id": str(user.tenant_id)})
    return {"delivered": ok}
