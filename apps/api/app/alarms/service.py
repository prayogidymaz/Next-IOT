"""Alarm lifecycle service."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from pydantic import JsonValue
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.alarms.fingerprint import alarm_fingerprint, dedup_key_from_details
from app.alarms.schemas import (
    AlarmCommentRequest,
    AlarmCreateRequest,
    AlarmHistoryItem,
    AlarmHistoryResponse,
    AlarmItem,
    AlarmListResponse,
    AlarmNoteRequest,
)
from app.alarms.state_machine import can_transition
from app.auth.context import CurrentUser
from app.models.alarm import Alarm, AlarmHistory, AlarmHistoryAction, AlarmStatus
from app.types.json_types import JsonObject

logger = logging.getLogger(__name__)


def _details_json(details: dict[str, object]) -> dict[str, JsonValue]:
    out: JsonObject = {}
    for key, value in details.items():
        if isinstance(key, str) and (
            isinstance(value, str | int | float | bool | list | dict) or value is None
        ):
            out[key] = value
    return out


def _to_alarm_item(row: Alarm) -> AlarmItem:
    return AlarmItem(
        id=row.id,
        tenant_id=row.tenant_id,
        device_id=row.device_id,
        alarm_type=row.alarm_type,
        severity=row.severity,
        status=row.status,
        title=row.title,
        message=row.message,
        details=_details_json(row.details),
        source=row.source,
        rule_id=row.rule_id,
        fingerprint=row.fingerprint,
        occurred_at=row.occurred_at,
        acknowledged_at=row.acknowledged_at,
        acknowledged_by_user_id=row.acknowledged_by_user_id,
        resolved_at=row.resolved_at,
        resolved_by_user_id=row.resolved_by_user_id,
        cleared_at=row.cleared_at,
        escalation_count=row.escalation_count,
    )


async def _append_history(
    db: AsyncSession,
    alarm_id: uuid.UUID,
    action: str,
    *,
    actor_user_id: uuid.UUID | None = None,
    note: str | None = None,
) -> None:
    db.add(
        AlarmHistory(
            alarm_id=alarm_id,
            action=action,
            actor_user_id=actor_user_id,
            note=note,
        )
    )


def _schedule_notifications(alarm_id: uuid.UUID) -> None:
    from app.config import settings
    from app.notifications.gateway_dispatcher import dispatch_alarm_notifications_task

    if not settings.alarm_notifications_enabled:
        return
    asyncio.create_task(dispatch_alarm_notifications_task(alarm_id))


async def upsert_alarm(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    device_id: uuid.UUID | None,
    alarm_type: str,
    severity: str,
    title: str,
    message: str | None,
    details: dict[str, JsonValue],
    source: str,
    rule_id: uuid.UUID | None = None,
    notify: bool = True,
) -> Alarm:
    details_store: dict[str, object] = dict(details)
    fp = alarm_fingerprint(
        tenant_id=tenant_id,
        device_id=device_id,
        alarm_type=alarm_type,
        dedup_key=dedup_key_from_details(details_store),
    )
    existing = await db.scalar(
        select(Alarm).where(Alarm.fingerprint == fp, Alarm.status == AlarmStatus.ACTIVE)
    )
    now = datetime.now(UTC)
    if existing is not None:
        existing.escalation_count += 1
        existing.occurred_at = now
        existing.message = message
        existing.details = details_store
        await _append_history(db, existing.id, AlarmHistoryAction.ESCALATED)
        await db.flush()
        if notify:
            _schedule_notifications(existing.id)
        return existing

    row = Alarm(
        tenant_id=tenant_id,
        device_id=device_id,
        alarm_type=alarm_type,
        severity=severity,
        status=AlarmStatus.ACTIVE,
        title=title,
        message=message,
        details=details_store,
        source=source,
        rule_id=rule_id,
        fingerprint=fp,
        occurred_at=now,
    )
    db.add(row)
    await db.flush()
    await _append_history(db, row.id, AlarmHistoryAction.CREATED)
    if notify:
        _schedule_notifications(row.id)
    return row


async def create_manual_alarm(
    db: AsyncSession,
    user: CurrentUser,
    payload: AlarmCreateRequest,
) -> AlarmItem:
    if payload.device_id is not None:
        from app.devices.service import _get_device_for_user

        await _get_device_for_user(db, payload.device_id, user)
    row = await upsert_alarm(
        db,
        tenant_id=user.tenant_id,
        device_id=payload.device_id,
        alarm_type=payload.alarm_type,
        severity=payload.severity.value,
        title=payload.title,
        message=payload.message,
        details=payload.details,
        source=payload.source,
    )
    return _to_alarm_item(row)


async def list_alarms(
    db: AsyncSession,
    user: CurrentUser,
    *,
    status_filter: str | None,
    severity_filter: str | None,
    device_id: uuid.UUID | None,
    since_hours: int | None,
) -> AlarmListResponse:
    query = select(Alarm)
    if not user.is_super_admin:
        query = query.where(Alarm.tenant_id == user.tenant_id)
    if status_filter:
        query = query.where(Alarm.status == status_filter)
    if severity_filter:
        query = query.where(Alarm.severity == severity_filter)
    if device_id:
        query = query.where(Alarm.device_id == device_id)
    if since_hours is not None and since_hours > 0:
        cutoff = datetime.now(UTC) - timedelta(hours=since_hours)
        query = query.where(Alarm.occurred_at >= cutoff)
    rows = list(await db.scalars(query.order_by(Alarm.occurred_at.desc()).limit(200)))
    return AlarmListResponse(items=[_to_alarm_item(r) for r in rows], total=len(rows))


async def _get_alarm_for_user(db: AsyncSession, user: CurrentUser, alarm_id: uuid.UUID) -> Alarm:
    query = select(Alarm).where(Alarm.id == alarm_id)
    if not user.is_super_admin:
        query = query.where(Alarm.tenant_id == user.tenant_id)
    row = await db.scalar(query)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alarm not found")
    return row


async def get_alarm(db: AsyncSession, user: CurrentUser, alarm_id: uuid.UUID) -> AlarmItem:
    return _to_alarm_item(await _get_alarm_for_user(db, user, alarm_id))


async def get_alarm_history(
    db: AsyncSession, user: CurrentUser, alarm_id: uuid.UUID
) -> AlarmHistoryResponse:
    await _get_alarm_for_user(db, user, alarm_id)
    rows = list(
        await db.scalars(
            select(AlarmHistory)
            .where(AlarmHistory.alarm_id == alarm_id)
            .order_by(AlarmHistory.occurred_at.asc())
        )
    )
    return AlarmHistoryResponse(
        items=[
            AlarmHistoryItem(
                id=r.id,
                action=r.action,
                actor_user_id=r.actor_user_id,
                note=r.note,
                occurred_at=r.occurred_at,
            )
            for r in rows
        ]
    )


async def acknowledge_alarm(
    db: AsyncSession,
    user: CurrentUser,
    alarm_id: uuid.UUID,
    payload: AlarmNoteRequest,
) -> AlarmItem:
    row = await _get_alarm_for_user(db, user, alarm_id)
    if not can_transition(row.status, AlarmStatus.ACKNOWLEDGED):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot acknowledge from current status")
    row.status = AlarmStatus.ACKNOWLEDGED
    row.acknowledged_at = datetime.now(UTC)
    row.acknowledged_by_user_id = user.user_id
    await _append_history(
        db, row.id, AlarmHistoryAction.ACKNOWLEDGED, actor_user_id=user.user_id, note=payload.note
    )
    await db.flush()
    return _to_alarm_item(row)


async def resolve_alarm(
    db: AsyncSession,
    user: CurrentUser,
    alarm_id: uuid.UUID,
    payload: AlarmNoteRequest,
) -> AlarmItem:
    row = await _get_alarm_for_user(db, user, alarm_id)
    if row.status == AlarmStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Alarm must be acknowledged before resolve",
        )
    if not can_transition(row.status, AlarmStatus.RESOLVED):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot resolve from current status")
    row.status = AlarmStatus.RESOLVED
    row.resolved_at = datetime.now(UTC)
    row.resolved_by_user_id = user.user_id
    await _append_history(
        db, row.id, AlarmHistoryAction.RESOLVED, actor_user_id=user.user_id, note=payload.note
    )
    await db.flush()
    return _to_alarm_item(row)


async def comment_alarm(
    db: AsyncSession,
    user: CurrentUser,
    alarm_id: uuid.UUID,
    payload: AlarmCommentRequest,
) -> AlarmItem:
    row = await _get_alarm_for_user(db, user, alarm_id)
    await _append_history(
        db, row.id, AlarmHistoryAction.COMMENTED, actor_user_id=user.user_id, note=payload.note
    )
    await db.flush()
    return _to_alarm_item(row)


async def clear_alarm(db: AsyncSession, alarm: Alarm, *, actor_user_id: uuid.UUID | None = None) -> None:
    if alarm.status == AlarmStatus.CLEARED:
        return
    if not can_transition(alarm.status, AlarmStatus.CLEARED):
        return
    alarm.status = AlarmStatus.CLEARED
    alarm.cleared_at = datetime.now(UTC)
    await _append_history(db, alarm.id, AlarmHistoryAction.CLEARED, actor_user_id=actor_user_id)


async def delete_alarm_hard(
    db: AsyncSession,
    user: CurrentUser,
    alarm_id: uuid.UUID,
    reason: str,
) -> None:
    row = await _get_alarm_for_user(db, user, alarm_id)
    logger.warning("Hard delete alarm %s by %s: %s", alarm_id, user.user_id, reason)
    await db.execute(delete(AlarmHistory).where(AlarmHistory.alarm_id == row.id))
    await db.delete(row)


