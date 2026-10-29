"""Workflow versioning tests."""

from __future__ import annotations

import uuid

import pytest
from app.types.json_types import JsonObject
from app.workflows.versioning.schemas import VersionDiffView
from app.workflows.versioning.service import _edge_keys, _node_ids


def test_node_ids_from_actions() -> None:
    snapshot: JsonObject = {
        "actions": [{"id": "a1", "type": "log_event"}, {"id": "a2", "type": "notification"}],
        "trigger": {"id": "t1", "type": "manual"},
    }
    assert _node_ids(snapshot) == {"a1", "a2", "t1"}


def test_node_ids_empty() -> None:
    assert _node_ids({}) == set()


def test_edge_keys_from_conditions() -> None:
    snapshot: JsonObject = {"conditions": [{"id": "c1"}, {"id": "c2"}]}
    keys = _edge_keys(snapshot)
    assert len(keys) == 2


def test_version_diff_view_defaults() -> None:
    diff = VersionDiffView()
    assert diff.added_nodes == []
    assert diff.removed_edges == []


def test_snapshot_child_order_irrelevant() -> None:
    a: JsonObject = {"actions": [{"id": "x", "type": "log_event"}]}
    b: JsonObject = {"actions": [{"id": "x", "type": "log_event"}]}
    assert _node_ids(a) == _node_ids(b)


@pytest.mark.asyncio
async def test_create_version_increments_number() -> None:
    from app.database import async_session
    from app.models.mesh_workflow import MeshWorkflow
    from app.models.tenant import Tenant
    from app.workflows.versioning.service import VersioningService

    async with async_session() as db:
        tenant = Tenant(name="Ver", slug=f"ver-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        mesh = MeshWorkflow(
            tenant_id=tenant.id,
            name="W",
            description="",
            enabled=False,
            definition={"trigger": {"type": "manual"}, "conditions": [], "actions": []},
        )
        db.add(mesh)
        await db.flush()
        service = VersioningService(db)
        v1 = await service.create_version(mesh.id, {"definition": mesh.definition}, tenant.id)
        v2 = await service.create_version(mesh.id, {"definition": mesh.definition}, tenant.id)
        assert v1.version_number == 1
        assert v2.version_number == 2


@pytest.mark.asyncio
async def test_list_versions_returns_desc() -> None:
    from app.auth.context import CurrentUser
    from app.auth.tiering import SecurityTier
    from app.database import async_session
    from app.models.mesh_workflow import MeshWorkflow
    from app.models.tenant import Tenant
    from app.workflows.versioning.service import VersioningService

    async with async_session() as db:
        tenant = Tenant(name="List", slug=f"list-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        mesh = MeshWorkflow(
            tenant_id=tenant.id,
            name="W",
            description="",
            enabled=False,
            definition={"trigger": {"type": "manual"}, "conditions": [], "actions": []},
        )
        db.add(mesh)
        await db.flush()
        service = VersioningService(db)
        await service.create_version(mesh.id, {"definition": {}}, tenant.id)
        await service.create_version(mesh.id, {"definition": {}}, tenant.id)
        user = CurrentUser(
            user_id=tenant.id,
            tenant_id=tenant.id,
            email="x@example.com",
            role="tenant_admin",
            security_tier=SecurityTier.PRO,
        )
        rows = await service.list_versions(mesh.id, user)
        assert len(rows) == 2
        assert rows[0].version_number >= rows[1].version_number


@pytest.mark.asyncio
async def test_get_active_version_none_initially() -> None:
    from app.database import async_session
    from app.models.mesh_workflow import MeshWorkflow
    from app.models.tenant import Tenant
    from app.workflows.versioning.service import VersioningService

    async with async_session() as db:
        tenant = Tenant(name="Act", slug=f"act-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        mesh = MeshWorkflow(tenant_id=tenant.id, name="W", description="", enabled=False, definition={})
        db.add(mesh)
        await db.flush()
        active = await VersioningService(db).get_active_version(mesh.id)
        assert active is None


@pytest.mark.asyncio
async def test_diff_detects_added_node() -> None:
    from app.auth.context import CurrentUser
    from app.auth.tiering import SecurityTier
    from app.database import async_session
    from app.models.mesh_workflow import MeshWorkflow
    from app.models.tenant import Tenant
    from app.workflows.versioning.service import VersioningService

    async with async_session() as db:
        tenant = Tenant(name="Diff", slug=f"diff-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        mesh = MeshWorkflow(tenant_id=tenant.id, name="W", description="", enabled=False, definition={})
        db.add(mesh)
        await db.flush()
        service = VersioningService(db)
        v1 = await service.create_version(
            mesh.id,
            {"definition": {"actions": [{"id": "a1", "type": "log_event"}], "conditions": []}},
            tenant.id,
        )
        v2 = await service.create_version(
            mesh.id,
            {
                "definition": {
                    "actions": [{"id": "a1", "type": "log_event"}, {"id": "a2", "type": "log_event"}],
                    "conditions": [],
                }
            },
            tenant.id,
        )
        user = CurrentUser(
            user_id=tenant.id,
            tenant_id=tenant.id,
            email="d@example.com",
            role="tenant_admin",
            security_tier=SecurityTier.PRO,
        )
        diff = await service.diff(v1.id, v2.id, user)
        assert "a2" in diff.added_nodes


@pytest.mark.asyncio
async def test_rollback_restores_name() -> None:
    from app.auth.context import CurrentUser
    from app.auth.tiering import SecurityTier
    from app.database import async_session
    from app.models.mesh_workflow import MeshWorkflow
    from app.models.tenant import Tenant
    from app.workflows.versioning.service import VersioningService

    async with async_session() as db:
        tenant = Tenant(name="Rb", slug=f"rb-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        mesh = MeshWorkflow(
            tenant_id=tenant.id,
            name="Original",
            description="",
            enabled=False,
            definition={"trigger": {"type": "manual"}, "conditions": [], "actions": []},
        )
        db.add(mesh)
        await db.flush()
        service = VersioningService(db)
        await service.create_version(
            mesh.id,
            {"name": "Original", "definition": mesh.definition, "description": "", "enabled": False},
            tenant.id,
        )
        mesh.name = "Changed"
        user = CurrentUser(
            user_id=tenant.id,
            tenant_id=tenant.id,
            email="r@example.com",
            role="tenant_admin",
            security_tier=SecurityTier.PRO,
        )
        restored = await service.rollback_to(mesh.id, 1, user)
        assert restored.name == "Original"
