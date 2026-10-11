"""Notification gateway settings API."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from app.auth.dependencies import RequireOperator
from app.deps import DbSession
from app.devices.rbac import RequireDeviceReader
from app.notifications import gateway_service
from app.notifications.gateway_schemas import (
    NotificationChannelCreate,
    NotificationChannelItem,
    NotificationChannelUpdate,
    NotificationLogItem,
    NotificationRuleCreate,
    NotificationRuleItem,
)

router = APIRouter(tags=["notification-gateway"])

channels_router = APIRouter(prefix="/api/v1/notification-channels")
rules_router = APIRouter(prefix="/api/v1/notification-rules")
log_router = APIRouter(prefix="/api/v1/notification-log")


@channels_router.get("", response_model=list[NotificationChannelItem])
async def list_channels(user: RequireDeviceReader, db: DbSession) -> list[NotificationChannelItem]:
    return await gateway_service.list_channels(db, user)


@channels_router.post("", response_model=NotificationChannelItem, status_code=201)
async def create_channel(
    payload: NotificationChannelCreate,
    user: RequireOperator,
    db: DbSession,
) -> NotificationChannelItem:
    return await gateway_service.create_channel(db, user, payload)


@channels_router.patch("/{channel_id}", response_model=NotificationChannelItem)
async def update_channel(
    channel_id: uuid.UUID,
    payload: NotificationChannelUpdate,
    user: RequireOperator,
    db: DbSession,
) -> NotificationChannelItem:
    return await gateway_service.update_channel(db, user, channel_id, payload)


@rules_router.get("", response_model=list[NotificationRuleItem])
async def list_rules(user: RequireDeviceReader, db: DbSession) -> list[NotificationRuleItem]:
    return await gateway_service.list_rules(db, user)


@rules_router.post("", response_model=NotificationRuleItem, status_code=201)
async def create_rule(
    payload: NotificationRuleCreate,
    user: RequireOperator,
    db: DbSession,
) -> NotificationRuleItem:
    return await gateway_service.create_rule(db, user, payload)


@log_router.get("", response_model=list[NotificationLogItem])
async def list_log(
    user: RequireDeviceReader,
    db: DbSession,
    alarm_id: Annotated[uuid.UUID | None, Query()] = None,
) -> list[NotificationLogItem]:
    return await gateway_service.list_notification_log(db, user, alarm_id)
