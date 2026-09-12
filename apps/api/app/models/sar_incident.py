import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SarIncidentType(StrEnum):
    PERSON_LOST = "PERSON_LOST"
    VEHICLE_CRASH = "VEHICLE_CRASH"
    DRONE_DOWN = "DRONE_DOWN"


class SarIncidentStatus(StrEnum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"


class SarIncident(Base):
    __tablename__ = "sar_incidents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    incident_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default=SarIncidentStatus.ACTIVE, index=True)
    target_lat: Mapped[float] = mapped_column(Float, nullable=False)
    target_lon: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False, default="critical")
    assigned_device_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True
    )
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    sar_grid: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tenant: Mapped["Tenant"] = relationship("Tenant")  # noqa: F821
    assigned_device: Mapped["Device | None"] = relationship("Device")  # noqa: F821
