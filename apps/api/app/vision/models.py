"""Vision ORM models."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class VisionDetection(Base):
    __tablename__ = "vision_detections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    labels_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    max_confidence: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    routing_action: Mapped[str] = mapped_column(String(32), nullable=False)
    species_guess: Mapped[str] = mapped_column(String(64), nullable=False)


class VisionFeedback(Base):
    __tablename__ = "vision_feedback"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    detection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vision_detections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    verdict: Mapped[str] = mapped_column(String(32), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    verified_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class VisionTenantConfig(Base):
    __tablename__ = "vision_tenant_config"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), primary_key=True
    )
    confidence_threshold: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False, default=Decimal("0.500"))
    auto_trigger_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
