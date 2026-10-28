"""Federation admin HTTP API."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Query, Response
from pydantic import BaseModel, Field

from app.auth.dependencies import RequireTenantAdmin
from app.deps import DbSession
from app.mesh.federation import service as federation_service

router = APIRouter(prefix="/api/v1/federation", tags=["mesh-federation"])


class PeerCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    url: str = Field(min_length=4, max_length=512)
    cert: str | None = None
    bidirectional: bool = True


@router.post("/peers")
async def post_peer(user: RequireTenantAdmin, db: DbSession, payload: PeerCreateRequest) -> dict[str, str]:
    row = await federation_service.create_peer(
        db,
        user,
        payload.name,
        payload.url,
        payload.cert,
        payload.bidirectional,
    )
    await db.commit()
    return {"id": str(row.id), "name": row.name}


@router.get("/peers")
async def get_peers(user: RequireTenantAdmin, db: DbSession) -> list[dict[str, object]]:
    rows = await federation_service.list_peers(db, user.tenant_id)
    return [
        {
            "id": str(row.id),
            "name": row.name,
            "url": row.url,
            "enabled": row.enabled,
            "bidirectional": row.bidirectional,
        }
        for row in rows
    ]


@router.delete("/peers/{peer_id}", status_code=204, response_class=Response)
async def delete_peer(user: RequireTenantAdmin, db: DbSession, peer_id: uuid.UUID) -> Response:
    await federation_service.delete_peer(db, user.tenant_id, peer_id)
    await db.commit()
    return Response(status_code=204)


@router.post("/sync-now")
async def post_sync_now(user: RequireTenantAdmin, db: DbSession) -> dict[str, int]:
    count = await federation_service.sync_now(db, user.tenant_id, site_name="local")
    await db.commit()
    return {"processed": count}


@router.get("/events-log")
async def get_events_log(
    user: RequireTenantAdmin,
    db: DbSession,
    origin: Annotated[str | None, Query()] = None,
    since: Annotated[datetime | None, Query()] = None,
) -> list[dict[str, object]]:
    rows = await federation_service.list_events_log(db, user.tenant_id, origin, since)
    return [
        {
            "id": str(row.id),
            "origin_site": row.origin_site,
            "event_id": row.event_id,
            "received_at": row.received_at.isoformat(),
            "processed": row.processed,
            "error": row.error,
        }
        for row in rows
    ]
