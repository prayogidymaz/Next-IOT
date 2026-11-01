"""Track workflow action outcomes for learning."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import StrEnum

from sqlalchemy.ext.asyncio import AsyncSession

from app.types.json_types import JsonObject


class ActionOutcome(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ActionLogEntry:
    workflow_id: uuid.UUID
    action_type: str
    params: JsonObject
    outcome: ActionOutcome
    time_to_resolve_ms: int | None
    resources_used: JsonObject


class ActionTracker:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._buffer: list[ActionLogEntry] = []

    async def log_action(
        self,
        workflow_id: uuid.UUID,
        action_type: str,
        params: JsonObject,
        outcome: ActionOutcome,
        time_to_resolve_ms: int | None = None,
        resources_used: JsonObject | None = None,
    ) -> None:
        entry = ActionLogEntry(
            workflow_id=workflow_id,
            action_type=action_type,
            params=params,
            outcome=outcome,
            time_to_resolve_ms=time_to_resolve_ms,
            resources_used=resources_used or {},
        )
        self._buffer.append(entry)
        _ = self._db  # persist to analytics table in future iteration

    def recent_entries(self) -> list[ActionLogEntry]:
        return list(self._buffer)
