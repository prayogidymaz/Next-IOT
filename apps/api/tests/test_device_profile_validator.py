from app.device_profiles.spec import (
    CommandDef,
    CommandParamInteger,
    CommandParamString,
    TelemetryKeyInteger,
    TelemetryKeyNumber,
    ThingModelSpec,
)
from app.device_profiles.validator import validate_command, validate_telemetry


def _sample_spec() -> ThingModelSpec:
    return ThingModelSpec(
        telemetry=[
            TelemetryKeyNumber(key="temp", label="Temp", data_type="number", min=0, max=50),
            TelemetryKeyInteger(key="level", label="Level", data_type="integer", min=1, max=5),
        ],
        attributes=[],
        commands=[
            CommandDef(
                key="configure",
                label="Configure",
                params=[
                    CommandParamString(key="name", data_type="string", required=True),
                    CommandParamInteger(key="slot", data_type="integer", required=False),
                ],
            ),
        ],
    )


def test_validate_telemetry_accepts_in_range() -> None:
    result = validate_telemetry(_sample_spec(), {"temp": 21.5, "level": 3})
    assert result.rejected == []
    assert result.unknown_keys == []
    assert result.accepted == {"temp": 21.5, "level": 3}


def test_validate_telemetry_rejects_out_of_range_number() -> None:
    result = validate_telemetry(_sample_spec(), {"temp": 999})
    assert len(result.rejected) == 1
    assert result.rejected[0].key == "temp"


def test_validate_telemetry_unknown_keys() -> None:
    result = validate_telemetry(_sample_spec(), {"mystery": 1})
    assert result.unknown_keys == ["mystery"]


def test_validate_command_requires_param() -> None:
    result = validate_command(_sample_spec(), "configure", {})
    assert result.valid is False
    assert any("name" in err for err in result.errors)


def test_validate_command_unknown_command() -> None:
    result = validate_command(_sample_spec(), "missing", {"name": "x"})
    assert result.valid is False
