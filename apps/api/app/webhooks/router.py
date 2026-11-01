"""Webhook registry API."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Response, status

from app.auth.dependencies import RequireAuth
from app.deps import DbSession
from app.webhooks import service
from app.webhooks.retry_queue import list_deliveries
from app.webhooks.schemas import WebhookCreate, WebhookUpdate, WebhookView
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


@router.get("", response_model=list[WebhookView])
async def list_hooks(user: RequireAuth, db: DbSession) -> list[WebhookView]:
    rows = await service.list_webhooks(db, user)
    return [WebhookView.model_validate(r) for r in rows]


@router.post("", response_model=WebhookView, status_code=201)
async def create_hook(user: RequireAuth, db: DbSession, payload: WebhookCreate) -> WebhookView:
    row = await service.create_webhook(db, user, payload)
    return WebhookView.model_validate(row)


@router.patch("/{webhook_id}", response_model=WebhookView)
async def patch_hook(user: RequireAuth, db: DbSession, webhook_id: uuid.UUID, payload: WebhookUpdate) -> WebhookView:
    row = await service.update_webhook(db, user, webhook_id, payload)
    return WebhookView.model_validate(row)


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_hook(user: RequireAuth, db: DbSession, webhook_id: uuid.UUID) -> Response:
    await service.delete_webhook(db, user, webhook_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{webhook_id}/test")
async def test_hook(user: RequireAuth, db: DbSession, webhook_id: uuid.UUID) -> dict[str, bool]:
    return await service.send_test(db, user, webhook_id)


class WebhookDeliveryView(BaseModel):
    id: uuid.UUID
    event_type: str
    status: str
    retry_count: int
    last_error: str | None
    created_at: datetime
    delivered_at: datetime | None

    model_config = {"from_attributes": True}


@router.get("/{webhook_id}/deliveries", response_model=list[WebhookDeliveryView])
async def webhook_deliveries(user: RequireAuth, db: DbSession, webhook_id: uuid.UUID) -> list[WebhookDeliveryView]:
    rows = await list_deliveries(db, webhook_id)
    return [WebhookDeliveryView.model_validate(r) for r in rows]
