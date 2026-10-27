"""Camera Gateway HTTP API."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.auth.dependencies import RequireAuth
from app.cameras.schemas import (
    CameraCreateRequest,
    CameraResponse,
    CameraSnapshotResponse,
    MotionIngestRequest,
    MotionIngestResponse,
)
from app.cameras.service import (
    create_camera,
    list_cameras,
    list_snapshots,
    record_motion_event,
    trigger_snapshot,
)
from app.deps import DbSession, RedisDep

router = APIRouter(prefix="/api/v1/cameras", tags=["cameras"])

FarmFilter = Annotated[uuid.UUID | None, Query()]
SnapshotLimit = Annotated[int, Query(ge=1, le=100)]


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def post_camera(user: RequireAuth, db: DbSession, payload: CameraCreateRequest) -> CameraResponse:
    row = await create_camera(db, user, payload)
    await db.commit()
    return row


@router.get("", response_model=list[CameraResponse])
async def get_cameras(user: RequireAuth, db: DbSession, farm_id: FarmFilter = None) -> list[CameraResponse]:
    return await list_cameras(db, user, farm_id)


@router.get("/{camera_id}/snapshot", response_model=CameraSnapshotResponse)
async def get_camera_snapshot(user: RequireAuth, db: DbSession, camera_id: uuid.UUID) -> CameraSnapshotResponse:
    snap = await trigger_snapshot(db, user, camera_id)
    await db.commit()
    return snap


@router.post("/{camera_id}/ingest-motion", response_model=MotionIngestResponse)
async def post_ingest_motion(
    user: RequireAuth,
    db: DbSession,
    redis: RedisDep,
    camera_id: uuid.UUID,
    payload: MotionIngestRequest,
) -> MotionIngestResponse:
    result = await record_motion_event(db, redis, user, camera_id, payload)
    await db.commit()
    return result


@router.get("/{camera_id}/snapshots", response_model=list[CameraSnapshotResponse])
async def get_camera_snapshots(
    user: RequireAuth,
    db: DbSession,
    camera_id: uuid.UUID,
    limit: SnapshotLimit = 10,
) -> list[CameraSnapshotResponse]:
    return await list_snapshots(db, user, camera_id, limit)
