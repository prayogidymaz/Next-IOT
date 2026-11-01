"""Sustainability ORM."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CarbonEntry(Base):
    __tablename__ = "carbon_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    site_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="SET NULL"), nullable=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    co2_equivalent_kg: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    auto_calculated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class WaterUsage(Base):
    __tablename__ = "water_usage"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    site_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="SET NULL"), nullable=True)
    plot_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("plots.id", ondelete="SET NULL"), nullable=True)
    liters_used: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EsgScorecard(Base):
    __tablename__ = "esg_scorecards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    period_month: Mapped[str] = mapped_column(String(7), nullable=False)
    environmental_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    social_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    governance_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    overall_grade: Mapped[str] = mapped_column(String(2), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    report_pdf_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
