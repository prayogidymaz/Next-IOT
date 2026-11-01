"""Reporting studio ORM."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ReportTemplate(Base):
    __tablename__ = "report_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    config_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class ReportSchedule(Base):
    __tablename__ = "report_schedules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("report_templates.id", ondelete="CASCADE"), nullable=False)
    cron_expression: Mapped[str] = mapped_column(String(64), nullable=False)
    recipients_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    format: Mapped[str] = mapped_column(String(16), nullable=False, default="pdf")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class ReportGeneration(Base):
    __tablename__ = "report_generations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("report_templates.id", ondelete="CASCADE"), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    file_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
