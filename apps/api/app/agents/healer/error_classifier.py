"""Rule-based workflow error classification."""

from __future__ import annotations

from app.agents.healer.types import ErrorCategory
from app.types.json_types import JsonObject


class ErrorClassifier:
    _RULES: tuple[tuple[tuple[str, ...], ErrorCategory], ...] = (
        (("device offline", "offline", "no telemetry"), ErrorCategory.DEVICE_OFFLINE),
        (("invalid payload", "schema", "validation error", "json"), ErrorCategory.SCHEMA_INVALID),
        (("timeout", "timed out", "deadline"), ErrorCategory.TIMEOUT),
        (("permission", "forbidden", "403", "unauthorized"), ErrorCategory.PERMISSION),
        (("not found", "missing dependency", "404"), ErrorCategory.DEPENDENCY_MISSING),
        (("rate limit", "429", "too many"), ErrorCategory.RATE_LIMITED),
    )

    def classify(self, error_message: str, context: JsonObject) -> ErrorCategory:
        text = error_message.lower()
        for keywords, category in self._RULES:
            if any(word in text for word in keywords):
                return category
        device_status = context.get("device_status")
        if device_status == "offline":
            return ErrorCategory.DEVICE_OFFLINE
        return ErrorCategory.UNKNOWN
