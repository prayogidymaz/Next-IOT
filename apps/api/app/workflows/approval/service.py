"""Workflow approval requests and policy."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.auth.rbac import UserRole, has_role
from app.models.mesh_workflow import MeshWorkflow
from app.workflows.approval.models import ApprovalRequestStatus, WorkflowApprovalPolicy, WorkflowApprovalRequest
from app.workflows.approval.schemas import ApprovalPolicyView, ApprovalRequestView


def _request_view(row: WorkflowApprovalRequest) -> ApprovalRequestView:
    return ApprovalRequestView(
        id=row.id,
        workflow_id=row.workflow_id,
        requested_by=row.requested_by,
        requested_at=row.requested_at,
        status=row.status,
        notes=row.notes,
        approved_by=row.approved_by,
        approved_at=row.approved_at,
        approval_notes=row.approval_notes,
    )


class ApprovalService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def _mesh_for_user(self, workflow_id: uuid.UUID, user: CurrentUser) -> MeshWorkflow:
        row = await self._db.scalar(select(MeshWorkflow).where(MeshWorkflow.id == workflow_id))
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
        if not user.is_super_admin and row.tenant_id != user.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return row

    async def check_policy(self, tenant_id: uuid.UUID) -> WorkflowApprovalPolicy:
        policy = await self._db.scalar(
            select(WorkflowApprovalPolicy).where(WorkflowApprovalPolicy.tenant_id == tenant_id)
        )
        if policy is None:
            policy = WorkflowApprovalPolicy(
                tenant_id=tenant_id,
                require_approval_for_production=False,
                min_approvers=1,
                approver_roles_json=["tenant_admin"],
            )
            self._db.add(policy)
            await self._db.flush()
        return policy

    async def get_policy_view(self, tenant_id: uuid.UUID) -> ApprovalPolicyView:
        policy = await self.check_policy(tenant_id)
        roles = policy.approver_roles_json if isinstance(policy.approver_roles_json, list) else []
        role_strings = [str(item) for item in roles]
        return ApprovalPolicyView(
            tenant_id=policy.tenant_id,
            require_approval_for_production=policy.require_approval_for_production,
            min_approvers=policy.min_approvers,
            approver_roles_json=role_strings,
        )

    async def update_policy(self, tenant_id: uuid.UUID, body: ApprovalPolicyView) -> ApprovalPolicyView:
        policy = await self.check_policy(tenant_id)
        policy.require_approval_for_production = body.require_approval_for_production
        policy.min_approvers = body.min_approvers
        policy.approver_roles_json = list(body.approver_roles_json)
        await self._db.flush()
        return await self.get_policy_view(tenant_id)

    async def request_approval(
        self,
        workflow_id: uuid.UUID,
        user_id: uuid.UUID,
        notes: str,
        user: CurrentUser,
    ) -> WorkflowApprovalRequest:
        await self._mesh_for_user(workflow_id, user)
        row = WorkflowApprovalRequest(
            workflow_id=workflow_id,
            requested_by=user_id,
            notes=notes,
            status=ApprovalRequestStatus.PENDING.value,
        )
        self._db.add(row)
        await self._db.flush()
        return row

    async def approve(
        self,
        request_id: uuid.UUID,
        approver_id: uuid.UUID,
        notes: str,
        user: CurrentUser,
    ) -> WorkflowApprovalRequest:
        row = await self._db.get(WorkflowApprovalRequest, request_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")
        mesh = await self._mesh_for_user(row.workflow_id, user)
        _ = mesh
        if row.status != ApprovalRequestStatus.PENDING.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request not pending")
        row.status = ApprovalRequestStatus.APPROVED.value
        row.approved_by = approver_id
        row.approved_at = datetime.now(tz=UTC)
        row.approval_notes = notes
        await self._db.flush()
        return row

    async def reject(
        self,
        request_id: uuid.UUID,
        approver_id: uuid.UUID,
        reason: str,
        user: CurrentUser,
    ) -> WorkflowApprovalRequest:
        row = await self._db.get(WorkflowApprovalRequest, request_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")
        await self._mesh_for_user(row.workflow_id, user)
        if row.status != ApprovalRequestStatus.PENDING.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request not pending")
        row.status = ApprovalRequestStatus.REJECTED.value
        row.approved_by = approver_id
        row.approved_at = datetime.now(tz=UTC)
        row.approval_notes = reason
        await self._db.flush()
        return row

    async def cancel(self, request_id: uuid.UUID, user_id: uuid.UUID, user: CurrentUser) -> WorkflowApprovalRequest:
        row = await self._db.get(WorkflowApprovalRequest, request_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")
        await self._mesh_for_user(row.workflow_id, user)
        if row.requested_by != user_id and not user.is_super_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only requester can cancel")
        if row.status != ApprovalRequestStatus.PENDING.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request not pending")
        row.status = ApprovalRequestStatus.CANCELLED.value
        await self._db.flush()
        return row

    async def get_pending_for_tenant(self, tenant_id: uuid.UUID) -> list[WorkflowApprovalRequest]:
        workflow_ids = await self._db.scalars(
            select(MeshWorkflow.id).where(MeshWorkflow.tenant_id == tenant_id)
        )
        ids = list(workflow_ids.all())
        if not ids:
            return []
        rows = await self._db.scalars(
            select(WorkflowApprovalRequest).where(
                WorkflowApprovalRequest.workflow_id.in_(ids),
                WorkflowApprovalRequest.status == ApprovalRequestStatus.PENDING.value,
            )
        )
        return list(rows.all())

    async def can_activate(self, workflow_id: uuid.UUID, user: CurrentUser) -> tuple[bool, str]:
        mesh = await self._mesh_for_user(workflow_id, user)
        policy = await self.check_policy(mesh.tenant_id)
        if not policy.require_approval_for_production:
            return True, ""
        approved = await self._db.scalar(
            select(WorkflowApprovalRequest).where(
                WorkflowApprovalRequest.workflow_id == workflow_id,
                WorkflowApprovalRequest.status == ApprovalRequestStatus.APPROVED.value,
            )
        )
        if approved is None:
            return False, "Production activation requires an approved change request"
        return True, ""

    def user_can_approve(self, user: CurrentUser, policy: WorkflowApprovalPolicy) -> bool:
        if user.is_super_admin:
            return True
        roles = policy.approver_roles_json if isinstance(policy.approver_roles_json, list) else []
        for role_raw in roles:
            role_str = str(role_raw)
            try:
                role = UserRole(role_str)
            except ValueError:
                continue
            if has_role(user.role, role):
                return True
        return has_role(user.role, UserRole.TENANT_ADMIN)
