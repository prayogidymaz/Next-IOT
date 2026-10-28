"""Federation persistence and sync orchestration."""

from __future__ import annotations

import uuid
from datetime import datetime

from app.auth.dependencies import CurrentUser
from app.mesh.federation.federation_client import FederationClient
from app.mesh.federation.messages import FederationMeshEvent
from app.mesh.federation.models import FederationEventsLog, FederationPeer
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_peer(
    db: AsyncSession,
    user: CurrentUser,
    name: str,
    url: str,
    cert_fingerprint: str | None,
    bidirectional: bool,
) -> FederationPeer:
    row = FederationPeer(
        tenant_id=user.tenant_id,
        name=name,
        url=url,
        cert_fingerprint=cert_fingerprint,
        bidirectional=bidirectional,
    )
    db.add(row)
    await db.flush()
    return row


async def list_peers(db: AsyncSession, tenant_id: uuid.UUID) -> list[FederationPeer]:
    return list((await db.scalars(select(FederationPeer).where(FederationPeer.tenant_id == tenant_id))).all())


async def delete_peer(db: AsyncSession, tenant_id: uuid.UUID, peer_id: uuid.UUID) -> None:
    row = await db.get(FederationPeer, peer_id)
    if row is None or row.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Peer not found")
    await db.delete(row)


async def sync_now(db: AsyncSession, tenant_id: uuid.UUID, site_name: str) -> int:
    peers = await list_peers(db, tenant_id)
    client = FederationClient(site_name)
    processed = 0
    for peer in peers:
        if not peer.enabled:
            continue
        event = FederationMeshEvent.from_local(site_name, "sync", uuid.uuid4(), {"peer": peer.name})
        await client.publish_remote(event)
        db.add(
            FederationEventsLog(
                tenant_id=tenant_id,
                origin_site=peer.name,
                event_id=str(uuid.uuid4()),
                processed=True,
            )
        )
        processed += 1
    await db.flush()
    return processed


async def list_events_log(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    origin: str | None,
    since: datetime | None,
) -> list[FederationEventsLog]:
    query = select(FederationEventsLog).where(FederationEventsLog.tenant_id == tenant_id)
    if origin is not None:
        query = query.where(FederationEventsLog.origin_site == origin)
    if since is not None:
        query = query.where(FederationEventsLog.received_at >= since)
    return list((await db.scalars(query.order_by(FederationEventsLog.received_at.desc()).limit(200))).all())
