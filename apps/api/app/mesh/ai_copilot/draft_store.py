"""Redis-backed storage for copilot workflow drafts (preview before commit)."""

from __future__ import annotations

import json
import uuid

from app.mesh.ai_copilot.workflow_draft import WorkflowDraft
from app.types.redis_client import RedisClient

_DRAFT_TTL_SECONDS = 3600
_KEY_PREFIX = "mesh:copilot:draft:"


def _key(draft_id: uuid.UUID) -> str:
    return f"{_KEY_PREFIX}{draft_id}"


async def save_draft(redis: RedisClient, draft: WorkflowDraft) -> None:
    payload = draft.model_dump_json()
    await redis.set(_key(draft.draft_id), payload, ex=_DRAFT_TTL_SECONDS)


async def load_draft(redis: RedisClient, draft_id: uuid.UUID) -> WorkflowDraft | None:
    raw = await redis.get(_key(draft_id))
    if raw is None:
        return None
    if isinstance(raw, bytes):
        text = raw.decode("utf-8")
    else:
        text = str(raw)
    return WorkflowDraft.model_validate_json(text)


async def delete_draft(redis: RedisClient, draft_id: uuid.UUID) -> None:
    await redis.delete(_key(draft_id))
