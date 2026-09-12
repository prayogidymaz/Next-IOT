import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GeofenceAction(StrEnum):
    WARN = "WARN"
    RTL = "RTL"
    LAND = "LAND"


class GeofenceZone(Base):
    __tablename__ = "geofence_zones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    polygon_coords: Mapped[list] = mapped_column(JSONB, nullable=False)
    max_altitude: Mapped[float] = mapped_column(Float, nullable=False, default=120.0)
    min_altitude: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    action_on_breach: Mapped[str] = mapped_column(String(8), nullable=False, default=GeofenceAction.WARN)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tenant: Mapped["Tenant"] = relationship("Tenant")  # noqa: F821
