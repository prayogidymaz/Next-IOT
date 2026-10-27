"""Camera registry, snapshots, motion → mesh events."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.auth.service import hash_password
from app.cameras.crypto import encrypt_camera_username
from app.cameras.models import Camera, CameraSnapshot
from app.cameras.schemas import (
    CameraCreateRequest,
    CameraResponse,
    CameraSnapshotResponse,
    MotionIngestRequest,
    MotionIngestResponse,
)
from app.mesh.event_bus import MeshDomain
from app.mesh.publisher import get_mesh_publisher
from app.mesh.schemas import MeshContext
from app.models.device import Device
from app.types.json_types import JsonObject
from app.types.redis_client import RedisClient

PLACEHOLDER_SNAPSHOT_BASE = "/api/v1/cameras/placeholder-snapshot.jpg"


def _camera_view(row: Camera) -> CameraResponse:
    return CameraResponse(
        id=row.id,
        tenant_id=row.tenant_id,
        name=row.name,
        rtsp_url=row.rtsp_url,
        location=row.location,
        farm_id=row.farm_id,
        plot_id=row.plot_id,
        physical_zone=row.physical_zone,
        mesh_device_id=row.mesh_device_id,
        enabled=row.enabled,
        last_seen_at=row.last_seen_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


async def create_camera(db: AsyncSession, user: CurrentUser, payload: CameraCreateRequest) -> CameraResponse:
    if payload.mesh_device_id is not None:
        device = await db.scalar(select(Device).where(Device.id == payload.mesh_device_id))
        if device is None or device.tenant_id != user.tenant_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid mesh_device_id")
    row = Camera(
        tenant_id=user.tenant_id,
        name=payload.name,
        rtsp_url=payload.rtsp_url,
        username_enc=encrypt_camera_username(payload.username),
        password_hash=hash_password(payload.password) if payload.password else "",
        location=payload.location,
        farm_id=payload.farm_id,
        plot_id=payload.plot_id,
        physical_zone=payload.physical_zone,
        mesh_device_id=payload.mesh_device_id,
        enabled=payload.enabled,
    )
    db.add(row)
    await db.flush()
    return _camera_view(row)


async def list_cameras(
    db: AsyncSession,
    user: CurrentUser,
    farm_id: uuid.UUID | None,
) -> list[CameraResponse]:
    stmt = select(Camera).where(Camera.tenant_id == user.tenant_id)
    if farm_id is not None:
        stmt = stmt.where(Camera.farm_id == farm_id)
    rows = await db.scalars(stmt.order_by(Camera.name))
    return [_camera_view(row) for row in rows.all()]


async def _get_camera(db: AsyncSession, user: CurrentUser, camera_id: uuid.UUID) -> Camera:
    row = await db.scalar(select(Camera).where(Camera.id == camera_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    if not user.is_super_admin and row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return row


async def trigger_snapshot(db: AsyncSession, user: CurrentUser, camera_id: uuid.UUID) -> CameraSnapshotResponse:
    camera = await _get_camera(db, user, camera_id)
    now = datetime.now(tz=UTC)
    snap = CameraSnapshot(
        camera_id=camera.id,
        captured_at=now,
        image_url=f"{PLACEHOLDER_SNAPSHOT_BASE}?camera={camera.id}&ts={int(now.timestamp())}",
        detection_json=None,
        event_id=None,
    )
    db.add(snap)
    camera.last_seen_at = now
    await db.flush()
    return CameraSnapshotResponse(
        id=snap.id,
        camera_id=snap.camera_id,
        captured_at=snap.captured_at,
        image_url=snap.image_url,
        detection_json=snap.detection_json,
        event_id=snap.event_id,
    )


async def list_snapshots(
    db: AsyncSession,
    user: CurrentUser,
    camera_id: uuid.UUID,
    limit: int,
) -> list[CameraSnapshotResponse]:
    await _get_camera(db, user, camera_id)
    rows = await db.scalars(
        select(CameraSnapshot)
        .where(CameraSnapshot.camera_id == camera_id)
        .order_by(CameraSnapshot.captured_at.desc())
        .limit(limit)
    )
    return [
        CameraSnapshotResponse(
            id=row.id,
            camera_id=row.camera_id,
            captured_at=row.captured_at,
            image_url=row.image_url,
            detection_json=row.detection_json,
            event_id=row.event_id,
        )
        for row in rows.all()
    ]


async def record_motion_event(
    db: AsyncSession,
    _redis: RedisClient,
    user: CurrentUser,
    camera_id: uuid.UUID,
    payload: MotionIngestRequest,
) -> MotionIngestResponse:
    camera = await _get_camera(db, user, camera_id)
    if not camera.enabled:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Camera disabled")
    if camera.mesh_device_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Camera has no mesh_device_id")

    captured = payload.timestamp or datetime.now(tz=UTC)
    detection: JsonObject = {
        "confidence": payload.confidence,
        "bbox": payload.bbox,
    }
    if payload.snapshot_base64:
        detection["snapshot_base64_present"] = True

    publisher = get_mesh_publisher()
    mesh_event_id: uuid.UUID | None = None
    if publisher is not None:
        context = MeshContext(
            physical_zone=camera.physical_zone,
            farm_id=camera.farm_id,
            plot_id=camera.plot_id,
        )
        mesh_event_id = await publisher.publish_event(
            db,
            tenant_id=camera.tenant_id,
            domain=MeshDomain.VISION,
            event_type="motion_detected",
            device_id=camera.mesh_device_id,
            payload={"confidence": payload.confidence, "bbox": payload.bbox, "camera_id": str(camera.id)},
            context=context,
        )

    snap = CameraSnapshot(
        camera_id=camera.id,
        captured_at=captured,
        image_url=f"{PLACEHOLDER_SNAPSHOT_BASE}?camera={camera.id}&motion=1",
        detection_json=detection,
        event_id=mesh_event_id,
    )
    db.add(snap)
    camera.last_seen_at = captured
    await db.flush()
    return MotionIngestResponse(snapshot_id=snap.id, mesh_event_id=mesh_event_id)
