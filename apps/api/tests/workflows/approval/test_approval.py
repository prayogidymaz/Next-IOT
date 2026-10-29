"""Workflow approval flow tests."""

from __future__ import annotations

import uuid

import pytest
from app.auth.context import CurrentUser
from app.auth.tiering import SecurityTier
from app.models.user import User
from app.workflows.approval.models import ApprovalRequestStatus
from app.workflows.approval.schemas import ApprovalPolicyView
from tests.workflows.conftest import workflow_current_user


def _user(tenant_id: uuid.UUID) -> CurrentUser:
    """Policy-only tests that do not persist approval rows."""
    return CurrentUser(
        user_id=uuid.uuid4(),
        tenant_id=tenant_id,
        email="u@example.com",
        role="tenant_admin",
        security_tier=SecurityTier.PRO,
    )


def test_approval_status_enum_values() -> None:
    assert ApprovalRequestStatus.PENDING.value == "pending"
    assert ApprovalRequestStatus.APPROVED.value == "approved"


def test_policy_view_defaults() -> None:
    view = ApprovalPolicyView(
        tenant_id=uuid.uuid4(),
        require_approval_for_production=False,
        min_approvers=1,
        approver_roles_json=["tenant_admin"],
    )
    assert view.min_approvers == 1


@pytest.mark.asyncio
async def test_check_policy_creates_default() -> None:
    from app.database import async_session
    from app.models.tenant import Tenant
    from app.workflows.approval.service import ApprovalService

    async with async_session() as db:
        tenant = Tenant(name="Pol", slug=f"pol-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        policy = await ApprovalService(db).check_policy(tenant.id)
        assert policy.tenant_id == tenant.id
        assert policy.require_approval_for_production is False


@pytest.mark.asyncio
async def test_request_approval_pending(workflow_seed_user: User) -> None:
    from app.database import async_session
    from app.models.mesh_workflow import MeshWorkflow
    from app.workflows.approval.service import ApprovalService

    async with async_session() as db:
        mesh = MeshWorkflow(
            tenant_id=workflow_seed_user.tenant_id,
            name="W",
            description="",
            enabled=False,
            definition={},
        )
        db.add(mesh)
        await db.flush()
        user = workflow_current_user(workflow_seed_user)
        row = await ApprovalService(db).request_approval(mesh.id, user.user_id, "ship it", user)
        assert row.status == ApprovalRequestStatus.PENDING.value


@pytest.mark.asyncio
async def test_can_activate_without_policy() -> None:
    from app.database import async_session
    from app.models.mesh_workflow import MeshWorkflow
    from app.models.tenant import Tenant
    from app.workflows.approval.service import ApprovalService

    async with async_session() as db:
        tenant = Tenant(name="Act", slug=f"act-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        mesh = MeshWorkflow(tenant_id=tenant.id, name="W", description="", enabled=False, definition={})
        db.add(mesh)
        await db.flush()
        ok, reason = await ApprovalService(db).can_activate(mesh.id, _user(tenant.id))
        assert ok is True
        assert reason == ""


@pytest.mark.asyncio
async def test_can_activate_blocked_when_required() -> None:
    from app.database import async_session
    from app.models.mesh_workflow import MeshWorkflow
    from app.models.tenant import Tenant
    from app.workflows.approval.service import ApprovalService

    async with async_session() as db:
        tenant = Tenant(name="Blk", slug=f"blk-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        mesh = MeshWorkflow(tenant_id=tenant.id, name="W", description="", enabled=False, definition={})
        db.add(mesh)
        await db.flush()
        service = ApprovalService(db)
        policy = await service.check_policy(tenant.id)
        policy.require_approval_for_production = True
        await db.flush()
        ok, reason = await ApprovalService(db).can_activate(mesh.id, _user(tenant.id))
        assert ok is False
        assert "approved" in reason.lower()


@pytest.mark.asyncio
async def test_approve_request(workflow_seed_user: User) -> None:
    from app.database import async_session
    from app.models.mesh_workflow import MeshWorkflow
    from app.workflows.approval.service import ApprovalService

    async with async_session() as db:
        mesh = MeshWorkflow(
            tenant_id=workflow_seed_user.tenant_id,
            name="W",
            description="",
            enabled=False,
            definition={},
        )
        db.add(mesh)
        await db.flush()
        service = ApprovalService(db)
        user = workflow_current_user(workflow_seed_user)
        req = await service.request_approval(mesh.id, user.user_id, "", user)
        approved = await service.approve(req.id, user.user_id, "ok", user)
        assert approved.status == ApprovalRequestStatus.APPROVED.value


@pytest.mark.asyncio
async def test_reject_request(workflow_seed_user: User) -> None:
    from app.database import async_session
    from app.models.mesh_workflow import MeshWorkflow
    from app.workflows.approval.service import ApprovalService

    async with async_session() as db:
        mesh = MeshWorkflow(
            tenant_id=workflow_seed_user.tenant_id,
            name="W",
            description="",
            enabled=False,
            definition={},
        )
        db.add(mesh)
        await db.flush()
        service = ApprovalService(db)
        user = workflow_current_user(workflow_seed_user)
        req = await service.request_approval(mesh.id, user.user_id, "", user)
        rejected = await service.reject(req.id, user.user_id, "no", user)
        assert rejected.status == ApprovalRequestStatus.REJECTED.value


@pytest.mark.asyncio
async def test_cancel_request(workflow_seed_user: User) -> None:
    from app.database import async_session
    from app.models.mesh_workflow import MeshWorkflow
    from app.workflows.approval.service import ApprovalService

    async with async_session() as db:
        mesh = MeshWorkflow(
            tenant_id=workflow_seed_user.tenant_id,
            name="W",
            description="",
            enabled=False,
            definition={},
        )
        db.add(mesh)
        await db.flush()
        service = ApprovalService(db)
        user = workflow_current_user(workflow_seed_user)
        req = await service.request_approval(mesh.id, user.user_id, "", user)
        cancelled = await service.cancel(req.id, user.user_id, user)
        assert cancelled.status == ApprovalRequestStatus.CANCELLED.value


@pytest.mark.asyncio
async def test_get_pending_for_tenant(workflow_seed_user: User) -> None:
    from app.database import async_session
    from app.models.mesh_workflow import MeshWorkflow
    from app.workflows.approval.service import ApprovalService

    async with async_session() as db:
        mesh = MeshWorkflow(
            tenant_id=workflow_seed_user.tenant_id,
            name="W",
            description="",
            enabled=False,
            definition={},
        )
        db.add(mesh)
        await db.flush()
        service = ApprovalService(db)
        user = workflow_current_user(workflow_seed_user)
        await service.request_approval(mesh.id, user.user_id, "", user)
        pending = await service.get_pending_for_tenant(workflow_seed_user.tenant_id)
        assert len(pending) == 1
