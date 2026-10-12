"""HTTP routes for Step 9C super-admin features."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy import select

from app.auth.dependencies import RequireSuperAdmin
from app.deps import DbSession
from app.models.platform_backup import PlatformBackup
from app.super_admin import step9c_service as svc
from app.super_admin.step9c_schemas import (
    BackupResponse,
    BackupRestoreRequest,
    BackupTriggerRequest,
    CommissionCalculateRequest,
    EmailTemplatePreviewRequest,
    EmailTemplatePreviewResponse,
    EmailTemplateResponse,
    EmailTemplateTestRequest,
    EmailTemplateUpdateRequest,
    ImpersonationActionResponse,
    ImpersonationSessionResponse,
    PartnerCommissionResponse,
    PartnerCreateRequest,
    PartnerReferralResponse,
    PartnerResponse,
    PartnerUpdateRequest,
    SupportTicketAssignRequest,
    SupportTicketDetailResponse,
    SupportTicketListItem,
    SupportTicketMessageCreateRequest,
    SupportTicketMessageResponse,
    SupportTicketStatsResponse,
    SupportTicketStatusRequest,
)

router = APIRouter(tags=["super-admin-step9c"])


@router.get("/email-templates", response_model=list[EmailTemplateResponse])
async def list_email_templates(user: RequireSuperAdmin, db: DbSession) -> list[EmailTemplateResponse]:
    return await svc.list_email_templates(db)


@router.get("/email-templates/{code}", response_model=EmailTemplateResponse)
async def get_email_template(user: RequireSuperAdmin, db: DbSession, code: str) -> EmailTemplateResponse:
    return await svc.get_email_template(db, code)


@router.put("/email-templates/{code}", response_model=EmailTemplateResponse)
async def put_email_template(
    user: RequireSuperAdmin, db: DbSession, code: str, payload: EmailTemplateUpdateRequest
) -> EmailTemplateResponse:
    return await svc.update_email_template(db, user, code, payload)


@router.post("/email-templates/{code}/preview", response_model=EmailTemplatePreviewResponse)
async def preview_email_template(
    user: RequireSuperAdmin, db: DbSession, code: str, payload: EmailTemplatePreviewRequest
) -> EmailTemplatePreviewResponse:
    return await svc.preview_email_template(db, code, payload.sample_variables)


@router.post("/email-templates/{code}/test")
async def test_email_template(
    user: RequireSuperAdmin, db: DbSession, code: str, payload: EmailTemplateTestRequest
) -> dict[str, str]:
    return await svc.test_send_email_template(db, user, code, payload.recipient_email, payload.sample_variables)


@router.get("/support-tickets/stats", response_model=SupportTicketStatsResponse)
async def support_stats(user: RequireSuperAdmin, db: DbSession) -> SupportTicketStatsResponse:
    return await svc.support_ticket_stats(db)


@router.get("/support-tickets", response_model=list[SupportTicketListItem])
async def list_support_tickets(
    user: RequireSuperAdmin,
    db: DbSession,
    status: str | None = None,
    priority: str | None = None,
    assigned_to: uuid.UUID | None = None,
    tenant_id: uuid.UUID | None = None,
    q: str | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[SupportTicketListItem]:
    return await svc.list_support_tickets(
        db,
        status_filter=status,
        priority=priority,
        assigned_to=assigned_to,
        tenant_id=tenant_id,
        search=q,
        offset=offset,
        limit=limit,
    )


@router.get("/support-tickets/{ticket_id}", response_model=SupportTicketDetailResponse)
async def get_support_ticket(
    user: RequireSuperAdmin,
    db: DbSession,
    ticket_id: uuid.UUID,
) -> SupportTicketDetailResponse:
    return await svc.get_support_ticket(db, ticket_id)


@router.post("/support-tickets/{ticket_id}/assign", status_code=204, response_class=Response)
async def assign_ticket(
    user: RequireSuperAdmin, db: DbSession, ticket_id: uuid.UUID, payload: SupportTicketAssignRequest
) -> Response:
    await svc.assign_ticket(db, user, ticket_id, payload.user_id)
    return Response(status_code=204)


@router.post("/support-tickets/{ticket_id}/status", status_code=204, response_class=Response)
async def ticket_status(
    user: RequireSuperAdmin, db: DbSession, ticket_id: uuid.UUID, payload: SupportTicketStatusRequest
) -> Response:
    await svc.set_ticket_status(db, user, ticket_id, payload.status)
    return Response(status_code=204)


@router.post("/support-tickets/{ticket_id}/messages", response_model=SupportTicketMessageResponse)
async def ticket_message(
    user: RequireSuperAdmin,
    db: DbSession,
    ticket_id: uuid.UUID,
    payload: SupportTicketMessageCreateRequest,
) -> SupportTicketMessageResponse:
    return await svc.add_ticket_message(db, user, ticket_id, payload.body, payload.is_internal, payload.attachments)


@router.get("/partners", response_model=list[PartnerResponse])
async def list_partners(user: RequireSuperAdmin, db: DbSession) -> list[PartnerResponse]:
    return await svc.list_partners(db)


@router.post("/partners", response_model=PartnerResponse, status_code=201)
async def create_partner(user: RequireSuperAdmin, db: DbSession, payload: PartnerCreateRequest) -> PartnerResponse:
    return await svc.create_partner(db, user, payload)


@router.put("/partners/{partner_id}", response_model=PartnerResponse)
async def update_partner(
    user: RequireSuperAdmin, db: DbSession, partner_id: uuid.UUID, payload: PartnerUpdateRequest
) -> PartnerResponse:
    return await svc.update_partner(db, user, partner_id, payload)


@router.get("/partners/{partner_id}/referrals", response_model=list[PartnerReferralResponse])
async def partner_referrals(
    user: RequireSuperAdmin,
    db: DbSession,
    partner_id: uuid.UUID,
) -> list[PartnerReferralResponse]:
    return await svc.list_partner_referrals(db, partner_id)


@router.get("/partners/{partner_id}/commissions", response_model=list[PartnerCommissionResponse])
async def partner_commissions(
    user: RequireSuperAdmin,
    db: DbSession,
    partner_id: uuid.UUID,
) -> list[PartnerCommissionResponse]:
    return await svc.list_partner_commissions(db, partner_id)


@router.post("/partners/{partner_id}/commissions/calculate", response_model=PartnerCommissionResponse)
async def calculate_commission(
    user: RequireSuperAdmin, db: DbSession, partner_id: uuid.UUID, payload: CommissionCalculateRequest
) -> PartnerCommissionResponse:
    return await svc.calculate_partner_commission(db, user, partner_id, payload.period_month)


@router.post("/partners/{partner_id}/commissions/{commission_id}/mark-paid", response_model=PartnerCommissionResponse)
async def mark_commission_paid(
    user: RequireSuperAdmin, db: DbSession, partner_id: uuid.UUID, commission_id: uuid.UUID
) -> PartnerCommissionResponse:
    return await svc.mark_commission_paid(db, user, partner_id, commission_id)


@router.get("/backups", response_model=list[BackupResponse])
async def list_backups(user: RequireSuperAdmin, db: DbSession) -> list[BackupResponse]:
    return await svc.list_backups(db)


@router.post("/backups/trigger", response_model=BackupResponse, status_code=201)
async def trigger_backup(user: RequireSuperAdmin, db: DbSession, payload: BackupTriggerRequest) -> BackupResponse:
    return await svc.trigger_backup(db, user, payload.backup_type)


@router.get("/backups/{backup_id}/download")
async def download_backup(user: RequireSuperAdmin, db: DbSession, backup_id: uuid.UUID) -> FileResponse:
    row = await db.scalar(select(PlatformBackup).where(PlatformBackup.id == backup_id))
    if row is None or not row.storage_path:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup not found")
    return FileResponse(row.storage_path, filename=f"backup-{backup_id}.dump")


@router.delete("/backups/{backup_id}", status_code=204, response_class=Response)
async def delete_backup(user: RequireSuperAdmin, db: DbSession, backup_id: uuid.UUID) -> Response:
    await svc.delete_backup(db, user, backup_id)
    return Response(status_code=204)


@router.post("/backups/{backup_id}/restore")
async def restore_backup(
    user: RequireSuperAdmin, db: DbSession, backup_id: uuid.UUID, payload: BackupRestoreRequest
) -> dict[str, str]:
    return await svc.restore_backup(db, user, backup_id, payload.confirm_token)


@router.get("/impersonation/sessions", response_model=list[ImpersonationSessionResponse])
async def list_impersonation_sessions(
    user: RequireSuperAdmin,
    db: DbSession,
    super_admin_id: uuid.UUID | None = None,
    tenant_id: uuid.UUID | None = None,
    from_ts: datetime | None = None,
    to_ts: datetime | None = None,
) -> list[ImpersonationSessionResponse]:
    return await svc.list_impersonation_sessions(
        db, super_admin_id=super_admin_id, tenant_id=tenant_id, from_ts=from_ts, to_ts=to_ts
    )


@router.get("/impersonation/sessions/{session_id}/actions", response_model=list[ImpersonationActionResponse])
async def impersonation_session_actions(
    user: RequireSuperAdmin, db: DbSession, session_id: uuid.UUID
) -> list[ImpersonationActionResponse]:
    return await svc.list_session_actions(db, session_id)
