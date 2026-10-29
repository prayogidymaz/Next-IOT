"""Workflow approval HTTP routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Response, status

from app.auth.dependencies import RequireAuth, RequireTenantAdmin
from app.deps import DbSession
from app.workflows.approval.schemas import (
    ApprovalDecisionBody,
    ApprovalPolicyUpdateBody,
    ApprovalPolicyView,
    ApprovalRequestBody,
    ApprovalRequestView,
)
from app.workflows.approval.service import ApprovalService, _request_view

workflow_router = APIRouter(prefix="/api/v1/workflows", tags=["workflow-approval"])
approval_router = APIRouter(prefix="/api/v1/approval", tags=["workflow-approval"])


@workflow_router.post("/{workflow_id}/approval/request", response_model=ApprovalRequestView, status_code=201)
async def request_workflow_approval(
    user: RequireAuth,
    db: DbSession,
    workflow_id: uuid.UUID,
    body: ApprovalRequestBody,
) -> ApprovalRequestView:
    service = ApprovalService(db)
    row = await service.request_approval(workflow_id, user.user_id, body.notes, user)
    return _request_view(row)


@approval_router.post("/{request_id}/approve", response_model=ApprovalRequestView)
async def approve_request(
    user: RequireAuth,
    db: DbSession,
    request_id: uuid.UUID,
    body: ApprovalDecisionBody,
) -> ApprovalRequestView:
    service = ApprovalService(db)
    policy = await service.check_policy(user.tenant_id)
    if not service.user_can_approve(user, policy):
        from fastapi import HTTPException

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an approver")
    row = await service.approve(request_id, user.user_id, body.notes, user)
    return _request_view(row)


@approval_router.post("/{request_id}/reject", response_model=ApprovalRequestView)
async def reject_request(
    user: RequireAuth,
    db: DbSession,
    request_id: uuid.UUID,
    body: ApprovalDecisionBody,
) -> ApprovalRequestView:
    service = ApprovalService(db)
    policy = await service.check_policy(user.tenant_id)
    if not service.user_can_approve(user, policy):
        from fastapi import HTTPException

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an approver")
    row = await service.reject(request_id, user.user_id, body.notes, user)
    return _request_view(row)


@approval_router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def cancel_request(
    user: RequireAuth,
    db: DbSession,
    request_id: uuid.UUID,
) -> Response:
    service = ApprovalService(db)
    await service.cancel(request_id, user.user_id, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@approval_router.get("/pending", response_model=list[ApprovalRequestView])
async def list_pending_approvals(user: RequireAuth, db: DbSession) -> list[ApprovalRequestView]:
    service = ApprovalService(db)
    rows = await service.get_pending_for_tenant(user.tenant_id)
    return [_request_view(row) for row in rows]


@approval_router.get("/policy", response_model=ApprovalPolicyView)
async def get_approval_policy(user: RequireAuth, db: DbSession) -> ApprovalPolicyView:
    service = ApprovalService(db)
    return await service.get_policy_view(user.tenant_id)


@approval_router.put("/policy", response_model=ApprovalPolicyView)
async def update_approval_policy(
    user: RequireTenantAdmin,
    db: DbSession,
    body: ApprovalPolicyUpdateBody,
) -> ApprovalPolicyView:
    service = ApprovalService(db)
    view = ApprovalPolicyView(
        tenant_id=user.tenant_id,
        require_approval_for_production=body.require_approval_for_production,
        min_approvers=body.min_approvers,
        approver_roles_json=body.approver_roles_json,
    )
    return await service.update_policy(user.tenant_id, view)
