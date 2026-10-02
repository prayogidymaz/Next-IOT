import pytest
from app.device_profiles.spec import (
    CommandDef,
    CommandParamInteger,
    TelemetryKeyEnum,
    TelemetryKeyInteger,
    TelemetryKeyNumber,
    ThingModelSpec,
)
from pydantic import ValidationError


def test_thing_model_spec_accepts_valid_telemetry_types() -> None:
    spec = ThingModelSpec(
        telemetry=[
            TelemetryKeyNumber(key="temp", label="Temp", data_type="number", min=0, max=100),
            TelemetryKeyInteger(key="count", label="Count", data_type="integer"),
            TelemetryKeyEnum(key="mode", label="Mode", data_type="enum", values=["a", "b"]),
        ],
        attributes=[],
        commands=[],
    )
    assert len(spec.telemetry) == 3


def test_thing_model_spec_rejects_invalid_key() -> None:
    with pytest.raises(ValidationError):
        TelemetryKeyNumber(key="Bad-Key", label="x", data_type="number")


def test_thing_model_spec_rejects_duplicate_telemetry_keys() -> None:
    with pytest.raises(ValidationError):
        ThingModelSpec(
            telemetry=[
                TelemetryKeyNumber(key="temp", label="A", data_type="number"),
                TelemetryKeyNumber(key="temp", label="B", data_type="number"),
            ],
            attributes=[],
            commands=[],
        )


def test_thing_model_spec_rejects_enum_without_values() -> None:
    with pytest.raises(ValidationError):
        TelemetryKeyEnum(key="mode", label="Mode", data_type="enum", values=[])


def test_command_def_unique_params() -> None:
    with pytest.raises(ValidationError):
        CommandDef(
            key="reset",
            label="Reset",
            params=[
                CommandParamInteger(key="delay", data_type="integer"),
                CommandParamInteger(key="delay", data_type="integer"),
            ],
        )
