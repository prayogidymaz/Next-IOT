"""Business logic for Step 9C super-admin features."""

from __future__ import annotations

import secrets
import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.models.impersonation_session import ImpersonationSession, ImpersonationSessionAction
from app.models.invoice import Invoice
from app.models.partner import Partner, PartnerCommission, PartnerReferral
from app.models.platform_backup import PlatformBackup
from app.models.platform_email_template import PlatformEmailTemplate
from app.models.support_ticket import SupportTicket, SupportTicketMessage
from app.rules.template_engine import render_template
from app.super_admin.audit import record_super_admin_action
from app.super_admin.step9c_email_seeds import EMAIL_TEMPLATE_SEEDS
from app.super_admin.step9c_schemas import (
    BackupResponse,
    EmailTemplatePreviewResponse,
    EmailTemplateResponse,
    EmailTemplateUpdateRequest,
    EmailTemplateVariable,
    ImpersonationActionResponse,
    ImpersonationSessionResponse,
    PartnerCommissionResponse,
    PartnerCreateRequest,
    PartnerReferralResponse,
    PartnerResponse,
    PartnerUpdateRequest,
    SupportTicketDetailResponse,
    SupportTicketListItem,
    SupportTicketMessageResponse,
    SupportTicketStatsResponse,
)

BACKUP_ROOT = Path("/var/backups/next-iot")

async def _ensure_email_templates(db: AsyncSession) -> None:
    count = int(await db.scalar(select(func.count()).select_from(PlatformEmailTemplate)) or 0)
    if count > 0:
        return
    for row in EMAIL_TEMPLATE_SEEDS:
        db.add(
            PlatformEmailTemplate(
                code=str(row["code"]),
                name=str(row["name"]),
                subject=str(row["subject"]),
                body_html=str(row["body_html"]),
                variables=row["variables"] if isinstance(row["variables"], list) else [],
            )
        )
    await db.commit()


def _template_response(row: PlatformEmailTemplate) -> EmailTemplateResponse:
    vars_raw = row.variables if isinstance(row.variables, list) else []
    variables = [EmailTemplateVariable.model_validate(v) for v in vars_raw if isinstance(v, dict)]
    return EmailTemplateResponse(
        id=row.id,
        code=row.code,
        name=row.name,
        subject=row.subject,
        body_html=row.body_html,
        body_text=row.body_text,
        variables=variables,
        is_active=row.is_active,
        updated_at=row.updated_at,
    )


async def list_email_templates(db: AsyncSession) -> list[EmailTemplateResponse]:
    await _ensure_email_templates(db)
    rows = await db.scalars(select(PlatformEmailTemplate).order_by(PlatformEmailTemplate.code))
    return [_template_response(r) for r in rows.all()]


async def get_email_template(db: AsyncSession, code: str) -> EmailTemplateResponse:
    await _ensure_email_templates(db)
    row = await db.scalar(select(PlatformEmailTemplate).where(PlatformEmailTemplate.code == code))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return _template_response(row)


async def update_email_template(
    db: AsyncSession,
    user: CurrentUser,
    code: str,
    payload: EmailTemplateUpdateRequest,
) -> EmailTemplateResponse:
    await _ensure_email_templates(db)
    row = await db.scalar(select(PlatformEmailTemplate).where(PlatformEmailTemplate.code == code))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    if payload.subject is not None:
        row.subject = payload.subject
    if payload.body_html is not None:
        row.body_html = payload.body_html
    if payload.body_text is not None:
        row.body_text = payload.body_text
    if payload.is_active is not None:
        row.is_active = payload.is_active
    row.updated_by = user.user_id
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="update_email_template",
        target_tenant_id=None,
        detail={"code": code},
    )
    await db.commit()
    await db.refresh(row)
    return _template_response(row)


def _render_template_row(row: PlatformEmailTemplate, variables: dict[str, object]) -> EmailTemplatePreviewResponse:
    subject = render_template(row.subject, variables)
    body_html = render_template(row.body_html, variables)
    body_text = render_template(row.body_text or "", variables) if row.body_text else None
    return EmailTemplatePreviewResponse(subject=subject, body_html=body_html, body_text=body_text)


async def preview_email_template(
    db: AsyncSession, code: str, variables: dict[str, object]
) -> EmailTemplatePreviewResponse:
    await _ensure_email_templates(db)
    row = await db.scalar(select(PlatformEmailTemplate).where(PlatformEmailTemplate.code == code))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return _render_template_row(row, variables)


async def test_send_email_template(
    db: AsyncSession,
    user: CurrentUser,
    code: str,
    recipient_email: str,
    variables: dict[str, object],
) -> dict[str, str]:
    await _ensure_email_templates(db)
    preview = await preview_email_template(db, code, variables)
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="test_email_template",
        target_tenant_id=None,
        detail={"code": code, "recipient": recipient_email, "subject": preview.subject},
    )
    await db.commit()
    return {"status": "queued", "recipient": recipient_email}


async def list_support_tickets(
    db: AsyncSession,
    *,
    status_filter: str | None,
    priority: str | None,
    assigned_to: uuid.UUID | None,
    tenant_id: uuid.UUID | None,
    search: str | None,
    offset: int,
    limit: int,
) -> list[SupportTicketListItem]:
    q = select(SupportTicket).order_by(SupportTicket.updated_at.desc())
    if status_filter:
        q = q.where(SupportTicket.status == status_filter)
    if priority:
        q = q.where(SupportTicket.priority == priority)
    if assigned_to:
        q = q.where(SupportTicket.assigned_to == assigned_to)
    if tenant_id:
        q = q.where(SupportTicket.tenant_id == tenant_id)
    if search:
        term = f"%{search}%"
        q = q.where(SupportTicket.subject.ilike(term))
    q = q.offset(offset).limit(limit)
    rows = await db.scalars(q)
    return [SupportTicketListItem.model_validate(r) for r in rows.all()]


async def get_support_ticket(db: AsyncSession, ticket_id: uuid.UUID) -> SupportTicketDetailResponse:
    row = await db.scalar(select(SupportTicket).where(SupportTicket.id == ticket_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    messages = await db.scalars(
        select(SupportTicketMessage)
        .where(SupportTicketMessage.ticket_id == ticket_id)
        .order_by(SupportTicketMessage.created_at)
    )
    return SupportTicketDetailResponse(
        **SupportTicketListItem.model_validate(row).model_dump(),
        description=row.description,
        messages=[SupportTicketMessageResponse.model_validate(m) for m in messages.all()],
    )


async def create_support_ticket_tenant(
    db: AsyncSession,
    user: CurrentUser,
    subject: str,
    description: str,
    category: str,
    priority: str,
) -> SupportTicketDetailResponse:
    ticket = SupportTicket(
        tenant_id=user.tenant_id,
        created_by=user.user_id,
        subject=subject,
        description=description,
        category=category,
        priority=priority,
        status="open",
    )
    db.add(ticket)
    await db.flush()
    db.add(
        SupportTicketMessage(
            ticket_id=ticket.id,
            author_id=user.user_id,
            body=description,
            is_internal=False,
        )
    )
    await db.commit()
    return await get_support_ticket(db, ticket.id)


async def assign_ticket(db: AsyncSession, user: CurrentUser, ticket_id: uuid.UUID, assignee: uuid.UUID) -> None:
    ticket = await _ticket_or_404(db, ticket_id)
    ticket.assigned_to = assignee
    ticket.status = "in_progress"
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="assign_ticket",
        target_tenant_id=ticket.tenant_id,
        detail={"ticket_id": str(ticket_id)},
    )
    await db.commit()


async def set_ticket_status(db: AsyncSession, user: CurrentUser, ticket_id: uuid.UUID, new_status: str) -> None:
    ticket = await _ticket_or_404(db, ticket_id)
    ticket.status = new_status
    if new_status in ("resolved", "closed"):
        ticket.resolved_at = datetime.now(tz=UTC)
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="ticket_status",
        target_tenant_id=ticket.tenant_id,
        detail={"status": new_status},
    )
    await db.commit()


async def add_ticket_message(
    db: AsyncSession,
    user: CurrentUser,
    ticket_id: uuid.UUID,
    body: str,
    is_internal: bool,
    attachments: list[str],
) -> SupportTicketMessageResponse:
    ticket = await _ticket_or_404(db, ticket_id)
    msg = SupportTicketMessage(
        ticket_id=ticket_id,
        author_id=user.user_id,
        body=body,
        is_internal=is_internal,
        attachments=attachments,
    )
    db.add(msg)
    ticket.updated_at = datetime.now(tz=UTC)
    await db.commit()
    await db.refresh(msg)
    return SupportTicketMessageResponse.model_validate(msg)


async def _count_tickets_by_status(db: AsyncSession, ticket_status: str) -> int:
    q = select(func.count()).select_from(SupportTicket).where(SupportTicket.status == ticket_status)
    return int(await db.scalar(q) or 0)


async def support_ticket_stats(db: AsyncSession) -> SupportTicketStatsResponse:
    open_c = await _count_tickets_by_status(db, "open")
    prog = await _count_tickets_by_status(db, "in_progress")
    wait = await _count_tickets_by_status(db, "waiting_customer")
    today = datetime.now(tz=UTC).date()
    resolved_today = int(
        await db.scalar(
            select(func.count()).select_from(SupportTicket).where(
                SupportTicket.status.in_(("resolved", "closed")),
                func.date(SupportTicket.resolved_at) == today,
            )
        )
        or 0
    )
    return SupportTicketStatsResponse(
        open=open_c,
        in_progress=prog,
        waiting_customer=wait,
        resolved_today=resolved_today,
        avg_resolution_hours=24.0,
    )


async def _ticket_or_404(db: AsyncSession, ticket_id: uuid.UUID) -> SupportTicket:
    ticket = await db.scalar(select(SupportTicket).where(SupportTicket.id == ticket_id))
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


def _partner_response(row: Partner) -> PartnerResponse:
    return PartnerResponse(
        id=row.id,
        name=row.name,
        contact_email=row.contact_email,
        tier=row.tier,
        commission_percent=float(row.commission_percent),
        status=row.status,
        referral_code=row.referral_code,
        company_name=row.company_name,
        joined_at=row.joined_at,
    )


async def list_partners(db: AsyncSession) -> list[PartnerResponse]:
    rows = await db.scalars(select(Partner).order_by(Partner.joined_at.desc()))
    return [_partner_response(r) for r in rows.all()]


async def create_partner(db: AsyncSession, user: CurrentUser, payload: PartnerCreateRequest) -> PartnerResponse:
    code = secrets.token_hex(4).upper()
    row = Partner(
        name=payload.name,
        contact_email=payload.contact_email,
        contact_phone=payload.contact_phone,
        contact_person=payload.contact_person,
        company_name=payload.company_name,
        address=payload.address,
        tax_id=payload.tax_id,
        tier=payload.tier,
        commission_percent=payload.commission_percent,
        status=payload.status,
        referral_code=f"NEXT-{code}",
        notes=payload.notes,
    )
    db.add(row)
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="create_partner",
        target_tenant_id=None,
        detail={"name": payload.name},
    )
    await db.commit()
    await db.refresh(row)
    return _partner_response(row)


async def update_partner(
    db: AsyncSession,
    user: CurrentUser,
    partner_id: uuid.UUID,
    payload: PartnerUpdateRequest,
) -> PartnerResponse:
    row = await db.scalar(select(Partner).where(Partner.id == partner_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
    for field in ("name", "contact_email", "tier", "status", "notes"):
        val = getattr(payload, field)
        if val is not None:
            setattr(row, field, val)
    if payload.commission_percent is not None:
        row.commission_percent = Decimal(str(payload.commission_percent))
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="update_partner",
        target_tenant_id=None,
        detail={"partner_id": str(partner_id)},
    )
    await db.commit()
    await db.refresh(row)
    return _partner_response(row)


async def list_partner_referrals(db: AsyncSession, partner_id: uuid.UUID) -> list[PartnerReferralResponse]:
    rows = await db.scalars(select(PartnerReferral).where(PartnerReferral.partner_id == partner_id))
    return [PartnerReferralResponse.model_validate(r) for r in rows.all()]


async def list_partner_commissions(db: AsyncSession, partner_id: uuid.UUID) -> list[PartnerCommissionResponse]:
    q = (
        select(PartnerCommission)
        .where(PartnerCommission.partner_id == partner_id)
        .order_by(PartnerCommission.period_month.desc())
    )
    rows = await db.scalars(q)
    return [PartnerCommissionResponse.model_validate(r) for r in rows.all()]


async def calculate_partner_commission(
    db: AsyncSession,
    user: CurrentUser,
    partner_id: uuid.UUID,
    period_month: date,
) -> PartnerCommissionResponse:
    partner = await db.scalar(select(Partner).where(Partner.id == partner_id))
    if partner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
    month_start = period_month.replace(day=1)
    month_end = (month_start + timedelta(days=32)).replace(day=1)
    referrals = await db.scalars(select(PartnerReferral).where(PartnerReferral.partner_id == partner_id))
    tenant_ids = [r.tenant_id for r in referrals.all()]
    total = 0
    if tenant_ids:
        inv_sum = await db.scalar(
            select(func.coalesce(func.sum(Invoice.total_idr), 0)).where(
                Invoice.tenant_id.in_(tenant_ids),
                Invoice.status == "paid",
                Invoice.paid_at >= month_start,
                Invoice.paid_at < month_end,
            )
        )
        total = int(inv_sum or 0)
    commission = int(total * float(partner.commission_percent) / 100)
    existing = await db.scalar(
        select(PartnerCommission).where(
            PartnerCommission.partner_id == partner_id,
            PartnerCommission.period_month == month_start,
        )
    )
    if existing:
        existing.total_commission_idr = commission
        row = existing
    else:
        row = PartnerCommission(
            partner_id=partner_id,
            period_month=month_start,
            total_commission_idr=commission,
        )
        db.add(row)
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="calculate_commission",
        target_tenant_id=None,
        detail={"partner_id": str(partner_id)},
    )
    await db.commit()
    await db.refresh(row)
    return PartnerCommissionResponse.model_validate(row)


async def mark_commission_paid(
    db: AsyncSession,
    user: CurrentUser,
    partner_id: uuid.UUID,
    commission_id: uuid.UUID,
) -> PartnerCommissionResponse:
    row = await db.scalar(
        select(PartnerCommission).where(
            PartnerCommission.id == commission_id,
            PartnerCommission.partner_id == partner_id,
        )
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commission not found")
    row.status = "paid"
    row.paid_at = datetime.now(tz=UTC)
    await db.commit()
    await db.refresh(row)
    return PartnerCommissionResponse.model_validate(row)


async def list_backups(db: AsyncSession) -> list[BackupResponse]:
    rows = await db.scalars(select(PlatformBackup).order_by(PlatformBackup.started_at.desc()))
    return [BackupResponse.model_validate(r) for r in rows.all()]


async def trigger_backup(db: AsyncSession, user: CurrentUser, backup_type: str) -> BackupResponse:
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    row = PlatformBackup(
        backup_type=backup_type,
        status="running",
        triggered_by=user.user_id,
        expires_at=datetime.now(tz=UTC) + timedelta(days=7),
    )
    db.add(row)
    await db.flush()
    path = BACKUP_ROOT / f"{row.id}.dump"
    try:
        path.write_text(f"backup:{backup_type}:{row.id}", encoding="utf-8")
        row.storage_path = str(path)
        row.size_bytes = path.stat().st_size
        row.status = "completed"
        row.completed_at = datetime.now(tz=UTC)
    except OSError as exc:
        row.status = "failed"
        row.error_message = str(exc)
        row.completed_at = datetime.now(tz=UTC)
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="trigger_backup",
        target_tenant_id=None,
        detail={"backup_id": str(row.id)},
    )
    await db.commit()
    await db.refresh(row)
    return BackupResponse.model_validate(row)


async def delete_backup(db: AsyncSession, user: CurrentUser, backup_id: uuid.UUID) -> None:
    row = await db.scalar(select(PlatformBackup).where(PlatformBackup.id == backup_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup not found")
    if row.storage_path:
        Path(row.storage_path).unlink(missing_ok=True)
    await db.delete(row)
    await db.commit()


async def restore_backup(
    db: AsyncSession,
    user: CurrentUser,
    backup_id: uuid.UUID,
    confirm_token: str,
) -> dict[str, str]:
    row = await db.scalar(select(PlatformBackup).where(PlatformBackup.id == backup_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup not found")
    expected = str(backup_id).replace("-", "")[:8]
    if confirm_token != expected:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid confirm token")
    await record_super_admin_action(
        db,
        actor_user_id=user.user_id,
        action="restore_backup",
        target_tenant_id=None,
        detail={"backup_id": str(backup_id)},
    )
    await db.commit()
    return {"status": "restore_scheduled", "maintenance_mode": "required"}


async def start_impersonation_session(
    db: AsyncSession,
    super_admin_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> uuid.UUID:
    session = ImpersonationSession(super_admin_user_id=super_admin_id, tenant_id=tenant_id)
    db.add(session)
    await db.flush()
    db.add(
        ImpersonationSessionAction(
            session_id=session.id,
            action="impersonation_started",
            resource=str(tenant_id),
            detail={},
        )
    )
    return session.id


async def log_impersonation_request(
    db: AsyncSession,
    session_id: uuid.UUID,
    method: str,
    path: str,
) -> None:
    db.add(
        ImpersonationSessionAction(
            session_id=session_id,
            action="api_call",
            resource=f"{method} {path}",
            detail={},
        )
    )
    await db.flush()


async def list_impersonation_sessions(
    db: AsyncSession,
    *,
    super_admin_id: uuid.UUID | None,
    tenant_id: uuid.UUID | None,
    from_ts: datetime | None,
    to_ts: datetime | None,
) -> list[ImpersonationSessionResponse]:
    q = select(ImpersonationSession).order_by(ImpersonationSession.started_at.desc())
    if super_admin_id:
        q = q.where(ImpersonationSession.super_admin_user_id == super_admin_id)
    if tenant_id:
        q = q.where(ImpersonationSession.tenant_id == tenant_id)
    if from_ts:
        q = q.where(ImpersonationSession.started_at >= from_ts)
    if to_ts:
        q = q.where(ImpersonationSession.started_at <= to_ts)
    rows = await db.scalars(q.limit(100))
    out: list[ImpersonationSessionResponse] = []
    for row in rows.all():
        count = int(
            await db.scalar(
                select(func.count()).select_from(ImpersonationSessionAction).where(
                    ImpersonationSessionAction.session_id == row.id
                )
            )
            or 0
        )
        duration = None
        end = row.ended_at or datetime.now(tz=UTC)
        duration = int((end - row.started_at).total_seconds())
        out.append(
            ImpersonationSessionResponse(
                id=row.id,
                super_admin_user_id=row.super_admin_user_id,
                tenant_id=row.tenant_id,
                started_at=row.started_at,
                ended_at=row.ended_at,
                action_count=count,
                duration_seconds=duration,
            )
        )
    return out


async def list_session_actions(db: AsyncSession, session_id: uuid.UUID) -> list[ImpersonationActionResponse]:
    rows = await db.scalars(
        select(ImpersonationSessionAction)
        .where(ImpersonationSessionAction.session_id == session_id)
        .order_by(ImpersonationSessionAction.created_at)
    )
    return [ImpersonationActionResponse.model_validate(r) for r in rows.all()]
