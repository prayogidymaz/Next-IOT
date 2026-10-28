"""Vision HTTP API."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Query

from app.auth.dependencies import RequireAuth
from app.deps import DbSession
from app.vision.schemas import (
    DetectRequest,
    DetectResponse,
    DetectionListItem,
    FeedbackRequest,
    VisionStatsResponse,
)
from app.vision.service import list_detections, run_detection, submit_feedback, vision_stats

router = APIRouter(prefix="/api/v1/vision", tags=["vision"])


@router.post("/detect", response_model=DetectResponse)
async def post_detect(user: RequireAuth, db: DbSession, payload: DetectRequest) -> DetectResponse:
    response = await run_detection(db, user, payload.device_id, payload.image_base64)
    await db.commit()
    return response


@router.post("/{detection_id}/feedback")
async def post_feedback(
    user: RequireAuth,
    db: DbSession,
    detection_id: uuid.UUID,
    payload: FeedbackRequest,
) -> dict[str, str]:
    row = await submit_feedback(db, user, detection_id, payload.verdict, payload.notes)
    await db.commit()
    return {"id": str(row.id), "verdict": row.verdict}


@router.get("/detections", response_model=list[DetectionListItem])
async def get_detections(
    user: RequireAuth,
    db: DbSession,
    device_id: Annotated[uuid.UUID | None, Query()] = None,
    since: Annotated[datetime | None, Query()] = None,
    species: Annotated[str | None, Query()] = None,
) -> list[DetectionListItem]:
    return await list_detections(db, user.tenant_id, device_id, since, species)


@router.get("/stats", response_model=VisionStatsResponse)
async def get_stats(user: RequireAuth, db: DbSession) -> VisionStatsResponse:
    return await vision_stats(db, user.tenant_id)
