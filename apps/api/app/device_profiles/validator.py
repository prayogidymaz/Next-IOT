"""Pure validation against a published thing-model spec (no I/O)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.device_profiles.spec import (
    CommandDef,
    CommandParamBoolean,
    CommandParamEnum,
    CommandParamInteger,
    CommandParamNumber,
    CommandParamString,
    TelemetryKeyBoolean,
    TelemetryKeyDef,
    TelemetryKeyEnum,
    TelemetryKeyInteger,
    TelemetryKeyNumber,
    TelemetryKeyString,
    ThingModelSpec,
)
from app.types.json_types import JsonValue, json_value_to_float


class RejectedTelemetryKey(BaseModel):
    key: str
    reason: str


class TelemetryValidationResult(BaseModel):
    accepted: dict[str, JsonValue] = Field(default_factory=dict)
    rejected: list[RejectedTelemetryKey] = Field(default_factory=list)
    unknown_keys: list[str] = Field(default_factory=list)


class CommandValidationResult(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)


def _telemetry_index(spec: ThingModelSpec) -> dict[str, TelemetryKeyDef]:
    return {entry.key: entry for entry in spec.telemetry}


def _command_index(spec: ThingModelSpec) -> dict[str, CommandDef]:
    return {entry.key: entry for entry in spec.commands}


def _validate_number_value(
    value: JsonValue,
    *,
    min_val: float | None,
    max_val: float | None,
) -> str | None:
    number = json_value_to_float(value)
    if number is None or isinstance(value, bool):
        return "expected number"
    if min_val is not None and number < min_val:
        return f"value below minimum {min_val}"
    if max_val is not None and number > max_val:
        return f"value above maximum {max_val}"
    return None


def _validate_integer_value(
    value: JsonValue,
    *,
    min_val: int | None,
    max_val: int | None,
) -> str | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return "expected integer"
    if min_val is not None and value < min_val:
        return f"value below minimum {min_val}"
    if max_val is not None and value > max_val:
        return f"value above maximum {max_val}"
    return None


def _validate_telemetry_entry(definition: TelemetryKeyDef, value: JsonValue) -> str | None:
    if isinstance(definition, TelemetryKeyNumber):
        return _validate_number_value(value, min_val=definition.min, max_val=definition.max)
    if isinstance(definition, TelemetryKeyInteger):
        return _validate_integer_value(value, min_val=definition.min, max_val=definition.max)
    if isinstance(definition, TelemetryKeyBoolean):
        return None if isinstance(value, bool) else "expected boolean"
    if isinstance(definition, TelemetryKeyString):
        return None if isinstance(value, str) else "expected string"
    if isinstance(definition, TelemetryKeyEnum):
        if not isinstance(value, str):
            return "expected enum string"
        if value not in definition.values:
            return f"unknown enum value; allowed: {definition.values}"
        return None
    return "unsupported telemetry definition"


def validate_telemetry(
    spec: ThingModelSpec,
    payload: dict[str, JsonValue],
) -> TelemetryValidationResult:
    known = _telemetry_index(spec)
    accepted: dict[str, JsonValue] = {}
    rejected: list[RejectedTelemetryKey] = []
    unknown_keys: list[str] = []

    for key, value in payload.items():
        definition = known.get(key)
        if definition is None:
            unknown_keys.append(key)
            continue
        reason = _validate_telemetry_entry(definition, value)
        if reason is None:
            accepted[key] = value
        else:
            rejected.append(RejectedTelemetryKey(key=key, reason=reason))

    return TelemetryValidationResult(accepted=accepted, rejected=rejected, unknown_keys=unknown_keys)


def _validate_command_param(
    param: CommandParamNumber
    | CommandParamInteger
    | CommandParamBoolean
    | CommandParamString
    | CommandParamEnum,
    value: JsonValue | None,
) -> str | None:
    if value is None:
        return "missing required parameter" if param.required else None
    if isinstance(param, CommandParamNumber):
        return _validate_number_value(value, min_val=param.min, max_val=param.max)
    if isinstance(param, CommandParamInteger):
        return _validate_integer_value(value, min_val=param.min, max_val=param.max)
    if isinstance(param, CommandParamBoolean):
        return None if isinstance(value, bool) else "expected boolean"
    if isinstance(param, CommandParamString):
        return None if isinstance(value, str) else "expected string"
    if isinstance(param, CommandParamEnum):
        if not isinstance(value, str):
            return "expected enum string"
        if value not in param.values:
            return f"unknown enum value; allowed: {param.values}"
        return None
    return "unsupported parameter definition"


def validate_command(
    spec: ThingModelSpec,
    command_key: str,
    params: dict[str, JsonValue],
) -> CommandValidationResult:
    command = _command_index(spec).get(command_key)
    if command is None:
        return CommandValidationResult(valid=False, errors=[f"unknown command: {command_key}"])

    errors: list[str] = []
    allowed = {p.key for p in command.params}
    for extra in params:
        if extra not in allowed:
            errors.append(f"unknown parameter: {extra}")

    for param in command.params:
        reason = _validate_command_param(param, params.get(param.key))
        if reason is not None:
            errors.append(f"{param.key}: {reason}")

    return CommandValidationResult(valid=len(errors) == 0, errors=errors)
