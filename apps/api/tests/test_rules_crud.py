import uuid

import pytest
from httpx import AsyncClient

from app.auth.security import hash_password
from app.database import async_session
from app.models.user import User

PASSWORD = "SecurePass123!"


async def _register_with_device(client: AsyncClient, slug: str, email: str) -> dict:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": f"T {slug}", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    assert reg.status_code == 201
    data = reg.json()
    token = data["tokens"]["access_token"]

    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Sensor", "device_type": "temp"},
    )
    assert create.status_code == 201
    device_id = create.json()["device"]["id"]

    return {"token": token, "tenant_id": data["tenant_id"], "device_id": device_id}


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_list_update_delete_rule(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_with_device(client, unique_slug, unique_email)

    create = await client.post(
        "/api/v1/rules",
        headers=_auth(ctx["token"]),
        json={
            "device_id": ctx["device_id"],
            "name": "High temp",
            "metric": "temperature",
            "operator": ">",
            "threshold": 30.0,
            "action_type": "alert",
        },
    )
    assert create.status_code == 201
    rule = create.json()
    assert rule["metric"] == "temperature"
    assert rule["is_active"] is True
    rule_id = rule["id"]

    listed = await client.get(
        f"/api/v1/devices/{ctx['device_id']}/rules",
        headers=_auth(ctx["token"]),
    )
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["id"] == rule_id

    updated = await client.patch(
        f"/api/v1/rules/{rule_id}",
        headers=_auth(ctx["token"]),
        json={"threshold": 35.0, "is_active": False},
    )
    assert updated.status_code == 200
    assert updated.json()["threshold"] == 35.0
    assert updated.json()["is_active"] is False

    deleted = await client.delete(f"/api/v1/rules/{rule_id}", headers=_auth(ctx["token"]))
    assert deleted.status_code == 204

    listed_after = await client.get(
        f"/api/v1/devices/{ctx['device_id']}/rules",
        headers=_auth(ctx["token"]),
    )
    assert len(listed_after.json()) == 0


@pytest.mark.asyncio
async def test_viewer_denied_rule_crud(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_with_device(client, unique_slug, unique_email)
    viewer_email = f"viewer-{uuid.uuid4().hex[:6]}@example.com"

    async with async_session() as session:
        session.add(
            User(
                tenant_id=uuid.UUID(ctx["tenant_id"]),
                email=viewer_email,
                password_hash=hash_password(PASSWORD),
                role="viewer",
            )
        )
        await session.commit()

    login = await client.post("/auth/login", json={"email": viewer_email, "password": PASSWORD})
    viewer_token = login.json()["access_token"]

    create = await client.post(
        "/api/v1/rules",
        headers=_auth(viewer_token),
        json={
            "device_id": ctx["device_id"],
            "name": "X",
            "metric": "temperature",
            "operator": ">",
            "threshold": 1.0,
        },
    )
    assert create.status_code == 403

    list_resp = await client.get(
        f"/api/v1/devices/{ctx['device_id']}/rules",
        headers=_auth(viewer_token),
    )
    assert list_resp.status_code == 403


@pytest.mark.asyncio
async def test_rule_tenant_isolation(client: AsyncClient):
    slug_a = f"a-{uuid.uuid4().hex[:6]}"
    slug_b = f"b-{uuid.uuid4().hex[:6]}"
    ctx_a = await _register_with_device(client, slug_a, f"a-{uuid.uuid4().hex[:6]}@example.com")
    ctx_b = await _register_with_device(client, slug_b, f"b-{uuid.uuid4().hex[:6]}@example.com")

    create_b = await client.post(
        "/api/v1/rules",
        headers=_auth(ctx_b["token"]),
        json={
            "device_id": ctx_b["device_id"],
            "name": "B rule",
            "metric": "humidity",
            "operator": "<",
            "threshold": 80.0,
        },
    )
    rule_b_id = create_b.json()["id"]

    cross_list = await client.get(
        f"/api/v1/devices/{ctx_b['device_id']}/rules",
        headers=_auth(ctx_a["token"]),
    )
    assert cross_list.status_code == 404

    cross_patch = await client.patch(
        f"/api/v1/rules/{rule_b_id}",
        headers=_auth(ctx_a["token"]),
        json={"is_active": False},
    )
    assert cross_patch.status_code == 404

    cross_delete = await client.delete(f"/api/v1/rules/{rule_b_id}", headers=_auth(ctx_a["token"]))
    assert cross_delete.status_code == 404


@pytest.mark.asyncio
async def test_create_rule_rejects_invalid_operator(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_with_device(client, unique_slug, unique_email)

    resp = await client.post(
        "/api/v1/rules",
        headers=_auth(ctx["token"]),
        json={
            "device_id": ctx["device_id"],
            "name": "Bad",
            "metric": "temperature",
            "operator": "!=",
            "threshold": 1.0,
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_rule_rejects_foreign_device(client: AsyncClient):
    slug_a = f"a-{uuid.uuid4().hex[:6]}"
    slug_b = f"b-{uuid.uuid4().hex[:6]}"
    ctx_a = await _register_with_device(client, slug_a, f"a-{uuid.uuid4().hex[:6]}@example.com")
    ctx_b = await _register_with_device(client, slug_b, f"b-{uuid.uuid4().hex[:6]}@example.com")

    resp = await client.post(
        "/api/v1/rules",
        headers=_auth(ctx_a["token"]),
        json={
            "device_id": ctx_b["device_id"],
            "name": "Cross",
            "metric": "temperature",
            "operator": ">",
            "threshold": 1.0,
        },
    )
    assert resp.status_code == 404
