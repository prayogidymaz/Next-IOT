import uuid

import pytest
from app.automation.pipeline_interpreter import PipelineInterpreterService
from app.models.automation_pipeline import AutomationPipeline


@pytest.fixture
def interpreter() -> PipelineInterpreterService:
    return PipelineInterpreterService()


def _sample_pipeline() -> AutomationPipeline:
    return AutomationPipeline(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        name="Geofence Auto Response",
        is_active=True,
        nodes_json=[
            {"id": "t1", "type": "TRIGGER", "subtype": "GEOFENCE_BREACH", "config": {}},
            {"id": "c1", "type": "CONDITION", "subtype": "BATTERY_ABOVE", "config": {"threshold": 10.0}},
            {"id": "a1", "type": "ACTION", "subtype": "MAVLINK_RTL", "config": {}},
        ],
        edges_json=[
            {"from": "t1", "to": "c1"},
            {"from": "c1", "to": "a1"},
        ],
    )


def test_evaluate_trigger_geofence_breach(interpreter: PipelineInterpreterService):
    assert interpreter.evaluate_trigger(
        "GEOFENCE_BREACH",
        "GEOFENCE_BREACH",
        {"anomaly_type": "geofence_breach"},
    )
    assert not interpreter.evaluate_trigger(
        "GEOFENCE_BREACH",
        "TELEMETRY_ANOMALY",
        {"anomaly_type": "geofence_breach"},
    )


def test_evaluate_condition_battery_above(interpreter: PipelineInterpreterService):
    assert interpreter.evaluate_condition(
        "BATTERY_ABOVE",
        {"threshold": 11.0},
        {"metrics": {"voltage": 12.4}},
    )
    assert not interpreter.evaluate_condition(
        "BATTERY_ABOVE",
        {"threshold": 11.0},
        {"metrics": {"voltage": 9.5}},
    )


def test_evaluate_condition_wind_speed_less_than(interpreter: PipelineInterpreterService):
    assert interpreter.evaluate_condition(
        "WIND_SPEED_LESS_THAN",
        {"threshold": 15.0},
        {"wind_speed_m_s": 8.0},
    )
    assert not interpreter.evaluate_condition(
        "WIND_SPEED_LESS_THAN",
        {"threshold": 15.0},
        {"wind_speed_m_s": 20.0},
    )


@pytest.mark.asyncio
async def test_run_pipeline_trigger_condition_action_chain(interpreter: PipelineInterpreterService):
    pipeline = _sample_pipeline()
    executed, steps = await interpreter.run_pipeline(
        pipeline,
        event_type="GEOFENCE_BREACH",
        context={
            "anomaly_type": "geofence_breach",
            "metrics": {"voltage": 12.0},
            "device_id": "dev-1",
        },
        dry_run=True,
    )
    assert executed is True
    assert len(steps) == 3
    assert steps[0].subtype == "GEOFENCE_BREACH"
    assert steps[0].matched is True
    assert steps[1].subtype == "BATTERY_ABOVE"
    assert steps[1].matched is True
    assert steps[2].subtype == "MAVLINK_RTL"
    assert steps[2].result.get("command") == "RTL"


def test_evaluate_telemetry_threshold_trigger(interpreter: PipelineInterpreterService):
    assert interpreter.evaluate_trigger(
        "TELEMETRY_THRESHOLD",
        "TELEMETRY_THRESHOLD",
        {"metrics": {"temperature": 31}},
        {"metric": "temperature", "operator": ">", "threshold": 30},
    )
    assert not interpreter.evaluate_trigger(
        "TELEMETRY_THRESHOLD",
        "TELEMETRY_THRESHOLD",
        {"metrics": {"temperature": 25}},
        {"metric": "temperature", "operator": ">", "threshold": 30},
    )


@pytest.mark.asyncio
async def test_run_pipeline_stops_when_condition_fails(interpreter: PipelineInterpreterService):
    pipeline = _sample_pipeline()
    executed, steps = await interpreter.run_pipeline(
        pipeline,
        event_type="GEOFENCE_BREACH",
        context={
            "anomaly_type": "geofence_breach",
            "metrics": {"voltage": 9.0},
        },
        dry_run=True,
    )
    assert executed is False
    assert len(steps) == 2
    assert steps[1].matched is False
