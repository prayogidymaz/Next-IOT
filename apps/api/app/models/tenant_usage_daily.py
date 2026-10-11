"""Daily usage snapshots per tenant."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TenantUsageDaily(Base):
    __tablename__ = "tenant_usage_daily"
    __table_args__ = (UniqueConstraint("tenant_id", "usage_date", name="uq_tenant_usage_daily_tenant_date"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    usage_date: Mapped[date] = mapped_column(Date, nullable=False)
    device_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    active_user_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    messages_count: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    api_calls_count: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    storage_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
