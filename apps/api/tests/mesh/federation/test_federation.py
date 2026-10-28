"""Mesh federation tests."""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from app.mesh.federation.federation_client import FederationClient
from app.mesh.federation.federation_server import AllowlistAuthenticator, FederationServer
from app.mesh.federation.messages import FederationMeshEvent

PASSWORD = "SecurePass123!"


def test_grpc_stubs_generated_from_proto() -> None:
    from app.mesh.federation import protocol_pb2
    from app.mesh.federation.protocol_pb2_grpc import MeshFederationStub

    event = protocol_pb2.MeshEvent(
        origin_site="a",
        event_type="t",
        device_id="d",
        payload_json="{}",
        timestamp=1,
        ttl=3,
    )
    assert event.ttl == 3
    assert MeshFederationStub is not None


@pytest.mark.asyncio
async def test_federation_server_authenticates_peer() -> None:
    cert = b"valid-cert-bytes"
    fp = __import__("hashlib").sha256(cert).hexdigest()
    server = FederationServer("site-a", AllowlistAuthenticator({fp}))

    async def _stream():
        yield FederationMeshEvent.from_local("site-b", "sensor.reading", uuid.uuid4(), {"domain": "sensor"})

    await server.handle_peer_stream(_stream(), cert)
    assert server.inbound.qsize() == 1


@pytest.mark.asyncio
async def test_federation_server_rejects_invalid_cert() -> None:
    server = FederationServer("site-a", AllowlistAuthenticator(set()))

    async def _stream():
        yield FederationMeshEvent.from_local("site-b", "sensor.reading", uuid.uuid4(), {})

    with pytest.raises(PermissionError):
        await server.handle_peer_stream(_stream(), b"bad-cert")


@pytest.mark.asyncio
async def test_federation_client_publish_event() -> None:
    client = FederationClient("local")
    event = FederationMeshEvent.from_local("local", "vision.detection", uuid.uuid4(), {"domain": "vision"})
    await client.publish_remote(event)
    received = []
    async for item in client.subscribe_remote(["vision"]):
        received.append(item)
        break
    assert received[0].event_type == "vision.detection"


@pytest.mark.asyncio
async def test_federation_bidirectional_sync() -> None:
    client = FederationClient("local")
    events = [FederationMeshEvent.from_local("peer", "motion.dispatch", uuid.uuid4(), {"domain": "motion"})]
    merged = await client.sync_devices_bidirectional(events)
    assert len(merged) == 1


@pytest.mark.asyncio
async def test_federation_event_filter() -> None:
    client = FederationClient("local")
    await client.publish_remote(FederationMeshEvent.from_local("p", "x", uuid.uuid4(), {"domain": "sensor"}))
    await client.publish_remote(FederationMeshEvent.from_local("p", "y", uuid.uuid4(), {"domain": "vision"}))
    seen: list[str] = []
    async for event in client.subscribe_remote(["vision"]):
        seen.append(str(event.payload().get("domain")))
        if len(seen) >= 1:
            break
    assert seen == ["vision"]


@pytest.mark.asyncio
async def test_federation_endpoints_require_admin(client: AsyncClient) -> None:
    assert (await client.get("/api/v1/federation/peers")).status_code == 401


@pytest.mark.asyncio
async def test_federation_peer_crud(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "Fed", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    create = await client.post(
        "/api/v1/federation/peers",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "farm-b", "url": "grpcs://farm-b:50051", "bidirectional": True},
    )
    assert create.status_code == 200
    listed = await client.get("/api/v1/federation/peers", headers={"Authorization": f"Bearer {token}"})
    assert len(listed.json()) >= 1


@pytest.mark.asyncio
async def test_federation_sync_now(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "FedSync", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    resp = await client.post("/api/v1/federation/sync-now", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_federation_events_log(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "FedLog", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    resp = await client.get("/api/v1/federation/events-log", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
