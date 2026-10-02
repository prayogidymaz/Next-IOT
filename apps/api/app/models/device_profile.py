from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.device import Device
    from app.models.tenant import Tenant


class ProfileDomain(StrEnum):
    SMART_HOME = "smart_home"
    SMART_FARMING = "smart_farming"
    CYBERDECK = "cyberdeck"
    DRONE = "drone"
    ROBOTICS = "robotics"
    INDUSTRIAL = "industrial"
    GENERIC = "generic"


class ProfileStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class DeviceProfile(Base):
    __tablename__ = "device_profiles"
    __table_args__ = (
        UniqueConstraint("tenant_id", "key", "version", name="uq_device_profiles_tenant_key_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    domain: Mapped[str] = mapped_column(String(32), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default=ProfileStatus.DRAFT)
    spec: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="device_profiles")  # noqa: F821
    devices: Mapped[list[Device]] = relationship("Device", back_populates="device_profile")  # noqa: F821
