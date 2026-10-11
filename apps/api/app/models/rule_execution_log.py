"""Audit log for rule engine executions."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RuleExecutionStatus(StrEnum):
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"


class RuleExecutionLog(Base):
    __tablename__ = "rule_execution_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    trigger_context: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(
        ENUM(
            RuleExecutionStatus.SUCCESS,
            RuleExecutionStatus.ERROR,
            RuleExecutionStatus.SKIPPED,
            name="rule_execution_status",
            create_type=False,
        ),
        nullable=False,
    )
    actions_executed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
