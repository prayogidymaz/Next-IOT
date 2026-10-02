import uuid

import pytest
from app.auth.security import hash_password
from app.database import async_session
from app.device_profiles.spec import TelemetryKeyBoolean, ThingModelSpec
from app.models.tenant_membership import TenantMembership
from app.models.user import User
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


def _minimal_spec() -> dict:
    spec = ThingModelSpec(
        telemetry=[TelemetryKeyBoolean(key="power", label="Power", data_type="boolean")],
        attributes=[],
        commands=[],
    )
    return spec.model_dump(mode="json")


async def _register(client: AsyncClient, slug: str, email: str) -> dict:
    resp = await client.post(
        "/auth/register",
        json={
            "tenant_name": f"Tenant {slug}",
            "tenant_slug": slug,
            "email": email,
            "password": PASSWORD,
        },
    )
    assert resp.status_code == 201
    return resp.json()


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _create_draft_profile(client: AsyncClient, token: str, key: str) -> dict:
    resp = await client.post(
        "/api/v1/device-profiles",
        headers=_auth(token),
        json={
            "key": key,
            "name": f"Profile {key}",
            "description": "test",
            "domain": "generic",
            "spec": _minimal_spec(),
        },
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_viewer_cannot_create_profile(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await _register(client, unique_slug, unique_email)
    tenant_id = uuid.UUID(reg["tenant_id"])
    viewer_email = f"viewer-{uuid.uuid4().hex[:6]}@example.com"
    async with async_session() as session:
        viewer = User(
            tenant_id=tenant_id,
            email=viewer_email,
            password_hash=hash_password(PASSWORD),
            role="viewer",
        )
        session.add(viewer)
        await session.flush()
        session.add(TenantMembership(user_id=viewer.id, tenant_id=tenant_id, role="viewer"))
        await session.commit()

    login = await client.post("/auth/login", json={"email": viewer_email, "password": PASSWORD})
    token = login.json()["access_token"]

    resp = await client.post(
        "/api/v1/device-profiles",
        headers=_auth(token),
        json={
            "key": "viewer_blocked",
            "name": "X",
            "domain": "generic",
            "spec": _minimal_spec(),
        },
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_patch_published_profile_returns_409(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await _register(client, unique_slug, unique_email)
    token = reg["tokens"]["access_token"]
    created = await _create_draft_profile(client, token, "immutable_test")
    profile_id = created["id"]

    pub = await client.post(f"/api/v1/device-profiles/{profile_id}/publish", headers=_auth(token))
    assert pub.status_code == 200

    patch = await client.patch(
        f"/api/v1/device-profiles/{profile_id}",
        headers=_auth(token),
        json={"name": "Changed"},
    )
    assert patch.status_code == 409


@pytest.mark.asyncio
async def test_publish_and_new_version(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await _register(client, unique_slug, unique_email)
    token = reg["tokens"]["access_token"]
    created = await _create_draft_profile(client, token, "versioned")
    profile_id = created["id"]

    await client.post(f"/api/v1/device-profiles/{profile_id}/publish", headers=_auth(token))
    nv = await client.post(f"/api/v1/device-profiles/{profile_id}/new-version", headers=_auth(token))
    assert nv.status_code == 201
    body = nv.json()
    assert body["version"] == 2
    assert body["status"] == "draft"


@pytest.mark.asyncio
async def test_archive_blocked_when_device_uses_profile(
    client: AsyncClient, unique_slug: str, unique_email: str
):
    reg = await _register(client, unique_slug, unique_email)
    token = reg["tokens"]["access_token"]
    created = await _create_draft_profile(client, token, "in_use")
    profile_id = uuid.UUID(created["id"])

    await client.post(f"/api/v1/device-profiles/{profile_id}/publish", headers=_auth(token))

    device = await client.post(
        "/api/v1/devices",
        headers=_auth(token),
        json={"name": "Dev1", "device_type": "sensor"},
    )
    assert device.status_code == 201
    device_id = device.json()["device"]["id"]

    assign = await client.patch(
        f"/api/v1/devices/{device_id}/profile",
        headers=_auth(token),
        json={"profile_id": str(profile_id)},
    )
    assert assign.status_code == 204

    archive = await client.post(
        f"/api/v1/device-profiles/{profile_id}/archive",
        headers=_auth(token),
    )
    assert archive.status_code == 409


@pytest.mark.asyncio
async def test_tenant_isolation_for_profiles(client: AsyncClient, unique_slug: str, unique_email: str):
    reg_a = await _register(client, unique_slug, unique_email)
    token_a = reg_a["tokens"]["access_token"]
    created = await _create_draft_profile(client, token_a, "tenant_a_only")
    profile_id = created["id"]

    slug_b = f"tenant-{uuid.uuid4().hex[:8]}"
    email_b = f"admin-{uuid.uuid4().hex[:8]}@example.com"
    reg_b = await _register(client, slug_b, email_b)
    token_b = reg_b["tokens"]["access_token"]

    get_resp = await client.get(f"/api/v1/device-profiles/{profile_id}", headers=_auth(token_b))
    assert get_resp.status_code == 404

    device = await client.post(
        "/api/v1/devices",
        headers=_auth(token_b),
        json={"name": "DevB", "device_type": "sensor"},
    )
    device_id = device.json()["device"]["id"]
    assign = await client.patch(
        f"/api/v1/devices/{device_id}/profile",
        headers=_auth(token_b),
        json={"profile_id": profile_id},
    )
    assert assign.status_code in {403, 404, 409}


@pytest.mark.asyncio
async def test_assign_requires_published_profile(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await _register(client, unique_slug, unique_email)
    token = reg["tokens"]["access_token"]
    created = await _create_draft_profile(client, token, "draft_only")
    profile_id = created["id"]

    device = await client.post(
        "/api/v1/devices",
        headers=_auth(token),
        json={"name": "DevDraft", "device_type": "sensor"},
    )
    device_id = device.json()["device"]["id"]

    assign = await client.patch(
        f"/api/v1/devices/{device_id}/profile",
        headers=_auth(token),
        json={"profile_id": profile_id},
    )
    assert assign.status_code == 409
