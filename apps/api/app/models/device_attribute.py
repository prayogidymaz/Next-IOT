import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DeviceAttributeScope(StrEnum):
    SERVER = "server"
    SHARED = "shared"
    CLIENT = "client"


class DeviceAttribute(Base):
    __tablename__ = "device_attributes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    scope: Mapped[str] = mapped_column(
        ENUM(
            DeviceAttributeScope.SERVER,
            DeviceAttributeScope.SHARED,
            DeviceAttributeScope.CLIENT,
            name="device_attribute_scope",
            create_type=False,
        ),
        nullable=False,
    )
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    value_json: Mapped[object] = mapped_column(JSONB, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    updated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    updated_source: Mapped[str] = mapped_column(String(32), nullable=False, server_default="api")
