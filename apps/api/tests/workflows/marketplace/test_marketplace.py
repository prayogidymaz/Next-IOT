"""Workflow marketplace tests."""

from __future__ import annotations

import uuid

import pytest
from app.workflows.marketplace.seed_templates import PRESEEDED_TEMPLATES, seed_template_rows


def test_preseeded_template_count() -> None:
    assert len(PRESEEDED_TEMPLATES) == 6


def test_preseeded_categories() -> None:
    categories = {item["category"] for item in PRESEEDED_TEMPLATES}
    assert categories == {"irrigation", "pest", "greenhouse", "aquaponics", "energy", "report"}


def test_seed_rows_length() -> None:
    rows = seed_template_rows(uuid.uuid4())
    assert len(rows) == 6


def test_seed_rows_have_snapshot() -> None:
    rows = seed_template_rows(uuid.uuid4())
    for row in rows:
        snap = row.get("snapshot_json")
        assert isinstance(snap, dict)
        definition = snap.get("definition")
        assert isinstance(definition, dict)


def test_irrigation_template_name() -> None:
    names = [item["name"] for item in PRESEEDED_TEMPLATES]
    assert "Smart Irrigation Kopi" in names


def test_pest_template_tags() -> None:
    pest = next(item for item in PRESEEDED_TEMPLATES if item["category"] == "pest")
    assert "spodoptera" in pest["tags"]


def test_snapshot_has_trigger_and_actions() -> None:
    snap = PRESEEDED_TEMPLATES[0]["snapshot_json"]
    definition = snap["definition"]
    assert "trigger" in definition
    assert "actions" in definition
    assert len(definition["actions"]) >= 1


@pytest.mark.asyncio
async def test_list_published_templates_empty() -> None:
    from app.database import async_session
    from app.workflows.marketplace.service import MarketplaceService

    async with async_session() as db:
        rows = await MarketplaceService(db).list_templates(None, "id", "downloads", 20)
        assert isinstance(rows, list)


@pytest.mark.asyncio
async def test_publish_template() -> None:
    from app.auth.context import CurrentUser
    from app.auth.tiering import SecurityTier
    from app.database import async_session
    from app.models.mesh_workflow import MeshWorkflow
    from app.models.tenant import Tenant
    from app.workflows.marketplace.service import MarketplaceService

    async with async_session() as db:
        tenant = Tenant(name="Pub", slug=f"pub-{uuid.uuid4().hex[:8]}")
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
        user = CurrentUser(
            user_id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="p@example.com",
            role="tenant_admin",
            security_tier=SecurityTier.PRO,
        )
        row = await MarketplaceService(db).publish(
            mesh.id,
            {"name": "Tpl", "category": "irrigation", "description": "d", "tags": []},
            user,
        )
        assert row.published is True


@pytest.mark.asyncio
async def test_download_increments_count() -> None:
    from app.auth.context import CurrentUser
    from app.auth.tiering import SecurityTier
    from app.database import async_session
    from app.models.tenant import Tenant
    from app.workflows.marketplace.models import WorkflowTemplate
    from app.workflows.marketplace.service import MarketplaceService

    async with async_session() as db:
        tenant = Tenant(name="Dl", slug=f"dl-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        tpl = WorkflowTemplate(
            name="T",
            description="",
            category="report",
            tags_json=[],
            author_tenant_id=tenant.id,
            snapshot_json={"definition": {"trigger": {"type": "manual"}, "conditions": [], "actions": []}},
            published=True,
        )
        db.add(tpl)
        await db.flush()
        user = CurrentUser(
            user_id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="d@example.com",
            role="tenant_admin",
            security_tier=SecurityTier.PRO,
        )
        await MarketplaceService(db).download(tpl.id, user, None)
        refreshed = await db.get(WorkflowTemplate, tpl.id)
        assert refreshed is not None
        assert refreshed.downloads_count == 1


@pytest.mark.asyncio
async def test_rate_template_updates_avg() -> None:
    from app.auth.context import CurrentUser
    from app.auth.tiering import SecurityTier
    from app.database import async_session
    from app.models.tenant import Tenant
    from app.workflows.marketplace.models import WorkflowTemplate
    from app.workflows.marketplace.service import MarketplaceService

    async with async_session() as db:
        tenant = Tenant(name="Rt", slug=f"rt-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        tpl = WorkflowTemplate(
            name="T",
            description="",
            category="energy",
            tags_json=[],
            author_tenant_id=tenant.id,
            snapshot_json={"definition": {}},
            published=True,
        )
        db.add(tpl)
        await db.flush()
        user = CurrentUser(
            user_id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="r@example.com",
            role="tenant_admin",
            security_tier=SecurityTier.PRO,
        )
        await MarketplaceService(db).rate(tpl.id, user, 5, "great")
        refreshed = await db.get(WorkflowTemplate, tpl.id)
        assert refreshed is not None
        assert refreshed.rating_count == 1
        assert refreshed.rating_avg == 5.0


@pytest.mark.asyncio
async def test_search_by_name() -> None:
    from app.database import async_session
    from app.models.tenant import Tenant
    from app.workflows.marketplace.models import WorkflowTemplate
    from app.workflows.marketplace.service import MarketplaceService

    async with async_session() as db:
        tenant = Tenant(name="Sr", slug=f"sr-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        db.add(
            WorkflowTemplate(
                name="UniqueAlphaName",
                description="find me",
                category="irrigation",
                tags_json=[],
                author_tenant_id=tenant.id,
                snapshot_json={"definition": {}},
                published=True,
            )
        )
        await db.flush()
        hits = await MarketplaceService(db).search("UniqueAlpha", {})
        assert any(row.name == "UniqueAlphaName" for row in hits)
