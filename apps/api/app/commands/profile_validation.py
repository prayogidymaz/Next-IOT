"""Thing-model command validation helpers (strict, no I/O)."""

from __future__ import annotations

from app.device_profiles.spec import ThingModelSpec
from app.device_profiles.validator import CommandValidationResult, validate_command
from app.telemetry.ingest_pipeline import profile_command_key
from app.types.json_types import JsonValue


def validate_command_for_profile(
    spec: ThingModelSpec,
    command_type: str,
    params: dict[str, JsonValue],
) -> CommandValidationResult:
    command_key = profile_command_key(command_type)
    return validate_command(spec, command_key, params)


def command_rejection_reason(result: CommandValidationResult) -> str:
    if not result.errors:
        return "validation"
    first = result.errors[0]
    if first.startswith("unknown command:"):
        return "unknown_command"
    return "invalid_params"
