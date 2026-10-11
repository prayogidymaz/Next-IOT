"""Alarm HTTP routes."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Query, Response

from app.alarms import service
from app.alarms.schemas import (
    AlarmCommentRequest,
    AlarmCreateRequest,
    AlarmHistoryResponse,
    AlarmItem,
    AlarmListResponse,
    AlarmNoteRequest,
    AlarmSeverityParam,
    AlarmStatusParam,
)
from app.auth.dependencies import RequireOperator, RequireSuperAdmin
from app.deps import DbSession
from app.devices.rbac import RequireDeviceReader

router = APIRouter(prefix="/api/v1/alarms", tags=["alarms"])

SinceHours = Annotated[int | None, Query(alias="since", description="Hours lookback e.g. 24")]


@router.get("", response_model=AlarmListResponse)
async def list_alarms(
    user: RequireDeviceReader,
    db: DbSession,
    status: Annotated[AlarmStatusParam | None, Query()] = None,
    severity: Annotated[AlarmSeverityParam | None, Query()] = None,
    device_id: Annotated[uuid.UUID | None, Query()] = None,
    since: SinceHours = None,
) -> AlarmListResponse:
    return await service.list_alarms(
        db,
        user,
        status_filter=status.value if status else None,
        severity_filter=severity.value if severity else None,
        device_id=device_id,
        since_hours=since,
    )


@router.get("/{alarm_id}", response_model=AlarmItem)
async def get_alarm(
    alarm_id: uuid.UUID,
    user: RequireDeviceReader,
    db: DbSession,
) -> AlarmItem:
    return await service.get_alarm(db, user, alarm_id)


@router.get("/{alarm_id}/history", response_model=AlarmHistoryResponse)
async def get_alarm_history(
    alarm_id: uuid.UUID,
    user: RequireDeviceReader,
    db: DbSession,
) -> AlarmHistoryResponse:
    return await service.get_alarm_history(db, user, alarm_id)


@router.post("", response_model=AlarmItem, status_code=201)
async def create_alarm(
    payload: AlarmCreateRequest,
    user: RequireOperator,
    db: DbSession,
) -> AlarmItem:
    return await service.create_manual_alarm(db, user, payload)


@router.post("/{alarm_id}/acknowledge", response_model=AlarmItem)
async def acknowledge_alarm(
    alarm_id: uuid.UUID,
    payload: AlarmNoteRequest,
    user: RequireOperator,
    db: DbSession,
) -> AlarmItem:
    return await service.acknowledge_alarm(db, user, alarm_id, payload)


@router.post("/{alarm_id}/resolve", response_model=AlarmItem)
async def resolve_alarm(
    alarm_id: uuid.UUID,
    payload: AlarmNoteRequest,
    user: RequireOperator,
    db: DbSession,
) -> AlarmItem:
    return await service.resolve_alarm(db, user, alarm_id, payload)


@router.post("/{alarm_id}/comment", response_model=AlarmItem)
async def comment_alarm(
    alarm_id: uuid.UUID,
    payload: AlarmCommentRequest,
    user: RequireOperator,
    db: DbSession,
) -> AlarmItem:
    return await service.comment_alarm(db, user, alarm_id, payload)


DeleteReason = Annotated[str, Query(min_length=1, max_length=500)]


@router.delete("/{alarm_id}", status_code=204, response_class=Response)
async def delete_alarm(
    alarm_id: uuid.UUID,
    reason: DeleteReason,
    user: RequireSuperAdmin,
    db: DbSession,
) -> Response:
    await service.delete_alarm_hard(db, user, alarm_id, reason)
    return Response(status_code=204)
