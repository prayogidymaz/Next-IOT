"""CRUD for notification channels, rules, and log."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from pydantic import JsonValue
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import CurrentUser
from app.models.notification_gateway import NotificationChannel, NotificationLog, NotificationRule
from app.notifications.gateway_schemas import (
    NotificationChannelCreate,
    NotificationChannelItem,
    NotificationChannelUpdate,
    NotificationLogItem,
    NotificationRuleCreate,
    NotificationRuleItem,
)
from app.types.json_types import JsonObject
from app.types.json_types import JsonValue as JsonValueType


def _json_value(value: object) -> JsonValueType | None:
    if isinstance(value, dict | list | str | int | float | bool) or value is None:
        return value
    return None


def _config_json_from_mapping(raw: dict[str, object]) -> dict[str, JsonValueType]:
    out: JsonObject = {}
    for key, value in raw.items():
        if isinstance(key, str):
            parsed = _json_value(value)
            if parsed is not None or value is None:
                out[key] = parsed
    return out


def _config_json_input(config: dict[str, JsonValue]) -> dict[str, object]:
    stored: dict[str, object] = {}
    for key, value in config.items():
        if isinstance(key, str):
            stored[key] = value
    return stored


async def list_channels(db: AsyncSession, user: CurrentUser) -> list[NotificationChannelItem]:
    rows = list(
        await db.scalars(
            select(NotificationChannel)
            .where(NotificationChannel.tenant_id == user.tenant_id)
            .order_by(NotificationChannel.created_at.desc())
        )
    )
    return [
        NotificationChannelItem(
            id=r.id,
            tenant_id=r.tenant_id,
            channel_type=r.channel_type,
            name=r.name,
            config=_config_json_from_mapping(r.config),
            is_active=r.is_active,
            created_at=r.created_at,
        )
        for r in rows
    ]


async def create_channel(
    db: AsyncSession, user: CurrentUser, payload: NotificationChannelCreate
) -> NotificationChannelItem:
    row = NotificationChannel(
        tenant_id=user.tenant_id,
        channel_type=payload.channel_type.value,
        name=payload.name,
        config=_config_json_input(payload.config),
        is_active=payload.is_active,
        created_by_user_id=user.user_id,
    )
    db.add(row)
    await db.flush()
    return NotificationChannelItem(
        id=row.id,
        tenant_id=row.tenant_id,
        channel_type=row.channel_type,
        name=row.name,
        config=_config_json_from_mapping(row.config),
        is_active=row.is_active,
        created_at=row.created_at,
    )


async def update_channel(
    db: AsyncSession,
    user: CurrentUser,
    channel_id: uuid.UUID,
    payload: NotificationChannelUpdate,
) -> NotificationChannelItem:
    row = await db.scalar(
        select(NotificationChannel).where(
            NotificationChannel.id == channel_id,
            NotificationChannel.tenant_id == user.tenant_id,
        )
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    if payload.name is not None:
        row.name = payload.name
    if payload.config is not None:
        row.config = _config_json_input(payload.config)
    if payload.is_active is not None:
        row.is_active = payload.is_active
    await db.flush()
    return NotificationChannelItem(
        id=row.id,
        tenant_id=row.tenant_id,
        channel_type=row.channel_type,
        name=row.name,
        config=_config_json_from_mapping(row.config),
        is_active=row.is_active,
        created_at=row.created_at,
    )


async def list_rules(db: AsyncSession, user: CurrentUser) -> list[NotificationRuleItem]:
    rows = list(
        await db.scalars(
            select(NotificationRule).where(NotificationRule.tenant_id == user.tenant_id)
        )
    )
    return [
        NotificationRuleItem(
            id=r.id,
            tenant_id=r.tenant_id,
            name=r.name,
            alarm_filter=_config_json_from_mapping(r.alarm_filter),
            channel_ids=list(r.channel_ids),
            throttle_seconds=r.throttle_seconds,
            escalation_minutes=r.escalation_minutes,
            is_active=r.is_active,
        )
        for r in rows
    ]


async def create_rule(
    db: AsyncSession, user: CurrentUser, payload: NotificationRuleCreate
) -> NotificationRuleItem:
    row = NotificationRule(
        tenant_id=user.tenant_id,
        name=payload.name,
        alarm_filter=_config_json_input(payload.alarm_filter),
        channel_ids=payload.channel_ids,
        throttle_seconds=payload.throttle_seconds,
        escalation_minutes=payload.escalation_minutes,
        is_active=payload.is_active,
    )
    db.add(row)
    await db.flush()
    return NotificationRuleItem(
        id=row.id,
        tenant_id=row.tenant_id,
        name=row.name,
        alarm_filter=_config_json_from_mapping(row.alarm_filter),
        channel_ids=list(row.channel_ids),
        throttle_seconds=row.throttle_seconds,
        escalation_minutes=row.escalation_minutes,
        is_active=row.is_active,
    )


async def list_notification_log(
    db: AsyncSession,
    user: CurrentUser,
    alarm_id: uuid.UUID | None,
) -> list[NotificationLogItem]:
    from app.models.alarm import Alarm

    query = select(NotificationLog).join(Alarm, NotificationLog.alarm_id == Alarm.id).where(
        Alarm.tenant_id == user.tenant_id
    )
    if alarm_id is not None:
        query = query.where(NotificationLog.alarm_id == alarm_id)
    rows = list(await db.scalars(query.order_by(NotificationLog.sent_at.desc().nullslast()).limit(200)))
    return [
        NotificationLogItem(
            id=r.id,
            alarm_id=r.alarm_id,
            channel_id=r.channel_id,
            channel_type=r.channel_type,
            status=r.status,
            error_message=r.error_message,
            retry_count=r.retry_count,
            sent_at=r.sent_at,
        )
        for r in rows
    ]
