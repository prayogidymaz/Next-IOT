import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DeviceStatus(StrEnum):
    PENDING = "pending"
    PROVISIONED = "provisioned"
    ONLINE = "online"
    OFFLINE = "offline"
    DEACTIVATED = "deactivated"


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=DeviceStatus.PENDING)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="devices")  # noqa: F821
    credentials: Mapped[list["DeviceCredential"]] = relationship(  # noqa: F821
        "DeviceCredential", back_populates="device", cascade="all, delete-orphan"
    )
    metadata_entries: Mapped[list["DeviceMetadata"]] = relationship(  # noqa: F821
        "DeviceMetadata", back_populates="device", cascade="all, delete-orphan"
    )
    telemetry_readings: Mapped[list["TelemetryReading"]] = relationship(  # noqa: F821
        "TelemetryReading", back_populates="device", cascade="all, delete-orphan"
    )
    rules: Mapped[list["Rule"]] = relationship(  # noqa: F821
        "Rule", back_populates="device", cascade="all, delete-orphan"
    )
