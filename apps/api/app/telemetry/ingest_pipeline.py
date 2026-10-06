"""Pure thing-model splitting for telemetry bulk ingest (strict typing, no I/O)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.device_profiles.spec import ThingModelSpec
from app.device_profiles.validator import validate_telemetry
from app.types.json_types import JsonValue


class RejectionReasonCode(StrEnum):
    OUT_OF_RANGE = "out_of_range"
    WRONG_TYPE = "wrong_type"
    ENUM_NOT_ALLOWED = "enum_not_allowed"


@dataclass(frozen=True)
class TelemetryRejectedMetric:
    key: str
    reason: str
    value: JsonValue


@dataclass(frozen=True)
class ProfileTelemetrySplit:
    metrics_to_persist: dict[str, JsonValue]
    rejected: tuple[TelemetryRejectedMetric, ...]
    unknown_keys: tuple[str, ...]
    accepted_key_count: int


def normalize_rejection_reason(raw_reason: str) -> str:
    lowered = raw_reason.lower()
    if "enum" in lowered or "allowed:" in lowered:
        return RejectionReasonCode.ENUM_NOT_ALLOWED
    if "minimum" in lowered or "maximum" in lowered or "below" in lowered or "above" in lowered:
        return RejectionReasonCode.OUT_OF_RANGE
    return RejectionReasonCode.WRONG_TYPE


def split_telemetry_for_profile(
    spec: ThingModelSpec | None,
    metrics: dict[str, JsonValue],
) -> ProfileTelemetrySplit:
    if spec is None:
        return ProfileTelemetrySplit(
            metrics_to_persist=dict(metrics),
            rejected=(),
            unknown_keys=(),
            accepted_key_count=len(metrics),
        )

    validation = validate_telemetry(spec, metrics)
    metrics_to_persist: dict[str, JsonValue] = dict(validation.accepted)
    for key in validation.unknown_keys:
        metrics_to_persist[key] = metrics[key]

    rejected = tuple(
        TelemetryRejectedMetric(
            key=entry.key,
            reason=normalize_rejection_reason(entry.reason),
            value=metrics[entry.key],
        )
        for entry in validation.rejected
    )
    return ProfileTelemetrySplit(
        metrics_to_persist=metrics_to_persist,
        rejected=rejected,
        unknown_keys=tuple(validation.unknown_keys),
        accepted_key_count=len(validation.accepted),
    )


_COMMAND_TYPE_PROFILE_KEY: dict[str, str] = {
    "RELAY_ON": "turn_on",
    "RELAY_OFF": "turn_off",
}


def profile_command_key(command_type: str) -> str:
    return _COMMAND_TYPE_PROFILE_KEY.get(command_type, command_type.lower())
