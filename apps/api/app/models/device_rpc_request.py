import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DeviceRpcStatus(StrEnum):
    PENDING = "pending"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    FAILED = "failed"


class DeviceRpcRequest(Base):
    __tablename__ = "device_rpc_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    method: Mapped[str] = mapped_column(String(64), nullable=False)
    params: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, server_default="{}")
    status: Mapped[str] = mapped_column(
        ENUM(
            DeviceRpcStatus.PENDING,
            DeviceRpcStatus.DELIVERED,
            DeviceRpcStatus.COMPLETED,
            DeviceRpcStatus.TIMEOUT,
            DeviceRpcStatus.FAILED,
            name="device_rpc_status",
            create_type=False,
        ),
        nullable=False,
        server_default=DeviceRpcStatus.PENDING,
    )
    response_json: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, server_default="30")
    requested_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
