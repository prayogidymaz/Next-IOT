"""Vision detection orchestration."""

from __future__ import annotations

import base64
import uuid
from datetime import UTC, datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.mesh.event_bus import MeshDomain
from app.mesh.publisher import get_mesh_publisher
from app.models.device import Device
from app.types.json_types import JsonObject
from app.vision.confidence_router import ConfidenceRouter
from app.vision.detector import PestDetector
from app.vision.feedback_loop import FalsePositiveFeedback
from app.vision.models import VisionDetection, VisionFeedback, VisionTenantConfig
from app.vision.schemas import DetectResponse, DetectionListItem, VisionStatsResponse


async def run_detection(
    db: AsyncSession,
    user: CurrentUser,
    device_id: uuid.UUID,
    image_base64: str,
) -> DetectResponse:
    device = await db.get(Device, device_id)
    if device is None or device.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    try:
        image_bytes = base64.b64decode(image_base64, validate=True)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid base64 image") from exc

    config = await db.scalar(select(VisionTenantConfig).where(VisionTenantConfig.tenant_id == user.tenant_id))
    threshold = float(config.confidence_threshold) if config else 0.5
    detector = PestDetector(confidence_threshold=threshold)
    result = detector.detect(image_bytes)
    router = ConfidenceRouter()
    routing = router.route(result, device_id, user.tenant_id)

    labels_json: JsonObject = {
        "bboxes": [b.model_dump() for b in result.bboxes],
        "labels": result.labels,
        "confidences": result.confidences,
    }
    row = VisionDetection(
        device_id=device_id,
        tenant_id=user.tenant_id,
        labels_json=labels_json,
        max_confidence=Decimal(str(result.max_confidence)),
        routing_action=routing.action.value,
        species_guess=result.species_guess,
    )
    db.add(row)
    await db.flush()

    publisher = get_mesh_publisher()
    if publisher is not None:
        payload: JsonObject = {
            "event": "vision.detection",
            "detection_id": str(row.id),
            "species_guess": result.species_guess,
            "max_confidence": result.max_confidence,
            "routing_action": routing.action.value,
            "severity": routing.severity,
        }
        await publisher.publish_event(
            db,
            tenant_id=user.tenant_id,
            domain=MeshDomain.VISION,
            event_type="detection",
            device_id=device_id,
            payload=payload,
        )
    return DetectResponse(detection_id=row.id, result=result, routing=routing)


async def list_detections(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    device_id: uuid.UUID | None,
    since: datetime | None,
    species: str | None,
) -> list[DetectionListItem]:
    query = select(VisionDetection).where(VisionDetection.tenant_id == tenant_id)
    if device_id is not None:
        query = query.where(VisionDetection.device_id == device_id)
    if since is not None:
        query = query.where(VisionDetection.timestamp >= since)
    if species is not None:
        query = query.where(VisionDetection.species_guess == species)
    query = query.order_by(VisionDetection.timestamp.desc()).limit(200)
    rows = list((await db.scalars(query)).all())
    return [
        DetectionListItem(
            id=row.id,
            device_id=row.device_id,
            timestamp=row.timestamp,
            labels_json=row.labels_json,
            max_confidence=float(row.max_confidence),
            routing_action=row.routing_action,
            species_guess=row.species_guess,
        )
        for row in rows
    ]


async def vision_stats(db: AsyncSession, tenant_id: uuid.UUID) -> VisionStatsResponse:
    feedback_rows = list(
        (await db.scalars(select(VisionFeedback).where(VisionFeedback.tenant_id == tenant_id))).all()
    )
    total = len(feedback_rows)
    tp = sum(1 for r in feedback_rows if r.verdict == "true_positive")
    fp = sum(1 for r in feedback_rows if r.verdict == "false_positive")
    fn = sum(1 for r in feedback_rows if r.verdict == "species_wrong")
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    fpr = fp / total if total else 0.0
    config = await db.scalar(select(VisionTenantConfig).where(VisionTenantConfig.tenant_id == tenant_id))
    threshold = float(config.confidence_threshold) if config else 0.5
    return VisionStatsResponse(
        tenant_id=tenant_id,
        precision=round(precision, 4),
        recall=round(recall, 4),
        false_positive_rate=round(fpr, 4),
        feedback_count=total,
        confidence_threshold=threshold,
    )


async def submit_feedback(
    db: AsyncSession,
    user: CurrentUser,
    detection_id: uuid.UUID,
    verdict: str,
    notes: str,
) -> VisionFeedback:
    detection = await db.get(VisionDetection, detection_id)
    if detection is None or detection.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detection not found")
    loop = FalsePositiveFeedback()
    return await loop.submit(db, detection_id, verdict, notes, user.user_id, user.tenant_id)
