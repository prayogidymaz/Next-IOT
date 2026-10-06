import secrets
import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings
from app.database import Base


class CredentialType(StrEnum):
    ACCESS_TOKEN = "access_token"
    MTLS_CERT = "mtls_cert"
    BASIC_AUTH = "basic_auth"


def generate_access_token() -> str:
    return secrets.token_urlsafe(settings.device_credential_token_length)


def generate_connection_client_id() -> str:
    return f"dev_{secrets.token_hex(4)}"


def device_short_id(device_id: uuid.UUID) -> str:
    return device_id.hex[:8]


class DeviceCredential(Base):
    __tablename__ = "device_credentials"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    credential_type: Mapped[CredentialType] = mapped_column(
        Enum(
            CredentialType,
            name="credential_type",
            native_enum=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=CredentialType.ACCESS_TOKEN,
    )
    access_token: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    client_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    secret_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_connected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    device: Mapped["Device"] = relationship("Device", back_populates="credentials")  # noqa: F821
