from app.commands.fail_safe import FAIL_SAFE_PRIORITY, FailSafeProtocol
from app.models.device_command import CommandType


def test_resolve_action_emergency_land_for_altitude():
    protocol = FailSafeProtocol()
    assert protocol.resolve_action("altitude_deviation", "critical") == CommandType.EMERGENCY_LAND


def test_resolve_action_return_to_home_for_voltage():
    protocol = FailSafeProtocol()
    assert protocol.resolve_action("voltage_drop", "critical") == CommandType.RETURN_TO_HOME


def test_resolve_action_ignored_for_warning():
    protocol = FailSafeProtocol()
    assert protocol.resolve_action("voltage_drop", "warning") is None


def test_build_params_includes_priority_flag():
    protocol = FailSafeProtocol()
    params = protocol.build_params(
        action=CommandType.RETURN_TO_HOME,
        reason="Critical voltage drop",
        anomaly_type="voltage_drop",
    )
    assert params["priority"] == FAIL_SAFE_PRIORITY
    assert params["fail_safe"] is True
    assert params["reason"] == "Critical voltage drop"
    assert params["action"] == CommandType.RETURN_TO_HOME
