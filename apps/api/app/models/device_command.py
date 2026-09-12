import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CommandType(StrEnum):
    GO_TO_WAYPOINT = "GO_TO_WAYPOINT"
    GO_TO_MISSION = "GO_TO_MISSION"
    RTL = "RTL"
    TAKEOFF = "TAKEOFF"
    LAND = "LAND"
    RETURN_TO_HOME = "RETURN_TO_HOME"
    EMERGENCY_LAND = "EMERGENCY_LAND"


class CommandStatus(StrEnum):
    QUEUED = "queued"
    DISPATCHED = "dispatched"
    FAILED = "failed"


class DeviceCommand(Base):
    __tablename__ = "device_commands"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    issued_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    command_type: Mapped[str] = mapped_column(String(64), nullable=False)
    params: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=CommandStatus.DISPATCHED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    dispatched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
