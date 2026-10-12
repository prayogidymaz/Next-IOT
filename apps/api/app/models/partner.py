"""Partner / reseller models."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Partner(Base):
    __tablename__ = "partners"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(320), nullable=False, default="")
    contact_phone: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    contact_person: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    company_name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    address: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tax_id: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    tier: Mapped[str] = mapped_column(String(16), nullable=False, default="silver")
    commission_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("10.00"))
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    referral_code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PartnerReferral(Base):
    __tablename__ = "partner_referrals"
    __table_args__ = (UniqueConstraint("partner_id", "tenant_id", name="uq_partner_referral_tenant"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"))
    referred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    first_payment_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_revenue_idr: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    total_commission_idr: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)


class PartnerCommission(Base):
    __tablename__ = "partner_commissions"
    __table_args__ = (UniqueConstraint("partner_id", "period_month", name="uq_partner_commission_period"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"))
    period_month: Mapped[date] = mapped_column(Date, nullable=False)
    total_commission_idr: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    invoice_url: Mapped[str | None] = mapped_column(Text, nullable=True)
