import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RuleOperator(StrEnum):
    GT = ">"
    LT = "<"
    EQ = "=="
    GTE = ">="
    LTE = "<="


class RuleActionType(StrEnum):
    ALERT = "alert"
    WEBHOOK = "webhook"


class RuleTriggerType(StrEnum):
    TELEMETRY = "telemetry"
    ATTRIBUTE_CHANGE = "attribute_change"
    ALARM = "alarm"
    SCHEDULE = "schedule"
    MANUAL = "manual"


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    device_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    metric: Mapped[str] = mapped_column(String(100), nullable=False)
    operator: Mapped[str] = mapped_column(String(10), nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False, default=RuleActionType.ALERT)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    trigger_type: Mapped[str] = mapped_column(
        ENUM(
            RuleTriggerType.TELEMETRY,
            RuleTriggerType.ATTRIBUTE_CHANGE,
            RuleTriggerType.ALARM,
            RuleTriggerType.SCHEDULE,
            RuleTriggerType.MANUAL,
            name="rule_trigger_type",
            create_type=False,
        ),
        nullable=False,
        default=RuleTriggerType.TELEMETRY,
    )
    trigger_config: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    condition_expr: Mapped[str | None] = mapped_column(Text, nullable=True)
    actions: Mapped[list[dict[str, object]]] = mapped_column(JSONB, nullable=False, default=list)
    last_executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    execution_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    device: Mapped["Device | None"] = relationship("Device", back_populates="rules")  # noqa: F821
