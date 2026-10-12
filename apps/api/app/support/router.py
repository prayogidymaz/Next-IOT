"""Tenant-facing support ticket API."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.auth.dependencies import RequireAuth
from app.deps import DbSession
from app.models.support_ticket import SupportTicket
from app.super_admin import step9c_service as svc
from app.super_admin.step9c_schemas import (
    SupportTicketCreateRequest,
    SupportTicketDetailResponse,
    SupportTicketListItem,
    SupportTicketMessageCreateRequest,
    SupportTicketMessageResponse,
)

router = APIRouter(prefix="/api/v1/support", tags=["support"])


@router.post("/tickets", response_model=SupportTicketDetailResponse, status_code=201)
async def create_ticket(
    user: RequireAuth,
    db: DbSession,
    payload: SupportTicketCreateRequest,
) -> SupportTicketDetailResponse:
    return await svc.create_support_ticket_tenant(
        db,
        user,
        payload.subject,
        payload.description,
        payload.category,
        payload.priority,
    )


@router.get("/tickets", response_model=list[SupportTicketListItem])
async def list_my_tickets(user: RequireAuth, db: DbSession) -> list[SupportTicketListItem]:
    return await svc.list_support_tickets(
        db,
        status_filter=None,
        priority=None,
        assigned_to=None,
        tenant_id=user.tenant_id,
        search=None,
        offset=0,
        limit=100,
    )


@router.get("/tickets/{ticket_id}", response_model=SupportTicketDetailResponse)
async def get_my_ticket(user: RequireAuth, db: DbSession, ticket_id: uuid.UUID) -> SupportTicketDetailResponse:
    ticket = await db.scalar(select(SupportTicket).where(SupportTicket.id == ticket_id))
    if ticket is None or ticket.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return await svc.get_support_ticket(db, ticket_id)


@router.post("/tickets/{ticket_id}/messages", response_model=SupportTicketMessageResponse)
async def add_my_message(
    user: RequireAuth,
    db: DbSession,
    ticket_id: uuid.UUID,
    payload: SupportTicketMessageCreateRequest,
) -> SupportTicketMessageResponse:
    ticket = await db.scalar(select(SupportTicket).where(SupportTicket.id == ticket_id))
    if ticket is None or ticket.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return await svc.add_ticket_message(db, user, ticket_id, payload.body, False, payload.attachments)
