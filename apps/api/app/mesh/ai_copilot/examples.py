"""Example NL prompts → mesh workflow DSL (mock / docs)."""

from __future__ import annotations

from app.mesh.workflow_schema import MeshWorkflowDefinition
from app.types.json_types import JsonObject

EXAMPLE_PROMPTS: tuple[str, ...] = (
    "Kalau drone deteksi hama di plot, dispatch drone cek + spray + notif WA",
    "Pagi hari jam 6, kirim summary kondisi semua farm ke petani",
    "Kalau soil moisture < 30% + no rain forecast, otomatis buka irigasi 15 menit",
    "Kalau ada motion di CCTV malam hari >jam 10, trigger alarm + record video 60s",
    "Weekly summary panen + yield analytics kirim ke owner Senin pagi",
)


def _irrigation_low_moisture() -> MeshWorkflowDefinition:
    return MeshWorkflowDefinition.model_validate(
        {
            "name": "Copilot Smart Irrigation",
            "description": "Open irrigation when soil moisture below 30% with dry forecast.",
            "enabled": True,
            "trigger": {
                "type": "mesh_event",
                "filter": {
                    "domain": "sensor",
                    "event_type": "threshold_exceeded",
                    "payload_match": {"metric": "moisture", "operator": "lt", "threshold": 30},
                },
            },
            "conditions": [
                {
                    "type": "attribute_true",
                    "device_resolver": {"capability": "can_predict_weather"},
                    "attribute": "no_rain_forecast_24h",
                }
            ],
            "actions": [
                {
                    "id": "irrigate",
                    "type": "trigger_device",
                    "device_resolver": {"capability": "can_control_valve"},
                    "command": "open_valve",
                    "params": {"duration_minutes": 15},
                },
                {
                    "id": "notify_farmer",
                    "type": "notification",
                    "channels": ["whatsapp"],
                    "template": "Irrigasi otomatis 15 menit — moisture < 30%.",
                },
            ],
        }
    )


def _pest_drone_response() -> MeshWorkflowDefinition:
    return MeshWorkflowDefinition.model_validate(
        {
            "name": "Copilot Pest Drone Response",
            "description": "Dispatch drone inspect + spray on pest detection.",
            "enabled": True,
            "trigger": {
                "type": "mesh_event",
                "filter": {
                    "domain": "vision",
                    "event_type": "motion_detected",
                    "payload_match": {"confidence": {"$gte": 0.75}},
                },
            },
            "actions": [
                {
                    "id": "dispatch_drone",
                    "type": "dispatch_device",
                    "device_resolver": {"capability": "can_fly_to", "zone": "plot_A"},
                    "command": "fly_to",
                    "params": {"mission": "pest_inspect"},
                },
                {
                    "id": "spray",
                    "type": "trigger_device",
                    "device_resolver": {"capability": "can_spray"},
                    "command": "start_spray",
                    "params": {"duration_seconds": 120},
                },
                {
                    "id": "wa",
                    "type": "notification",
                    "channels": ["whatsapp"],
                    "template": "Hama terdeteksi — drone dispatch + spray aktif.",
                },
            ],
        }
    )


def _morning_farm_summary() -> MeshWorkflowDefinition:
    return MeshWorkflowDefinition.model_validate(
        {
            "name": "Copilot Morning Farm Summary",
            "description": "Daily 06:00 farm summary notification.",
            "enabled": True,
            "trigger": {"type": "schedule", "filter": {"schedule_cron": "0 6 * * *"}},
            "actions": [
                {
                    "id": "summary",
                    "type": "notification",
                    "channels": ["whatsapp", "email"],
                    "template": "Ringkasan pagi: semua farm — moisture, alert, irigasi.",
                },
                {
                    "id": "log",
                    "type": "log_event",
                    "log_message": "Morning farm summary sent.",
                },
            ],
        }
    )


def _cctv_night_alarm() -> MeshWorkflowDefinition:
    return MeshWorkflowDefinition.model_validate(
        {
            "name": "Copilot CCTV Night Alarm",
            "description": "Night motion → alarm + record clip.",
            "enabled": True,
            "trigger": {
                "type": "mesh_event",
                "filter": {
                    "domain": "vision",
                    "event_type": "motion_detected",
                    "time_filter": {"after_hour": 22},
                },
            },
            "actions": [
                {
                    "id": "alarm",
                    "type": "create_alarm",
                    "alarm_type": "intrusion",
                    "severity": "high",
                    "title": "CCTV motion after 22:00",
                    "message": "Motion detected — recording 60s clip.",
                },
                {
                    "id": "record",
                    "type": "trigger_device",
                    "device_resolver": {"capability": "can_record_video"},
                    "command": "record_clip",
                    "params": {"duration_seconds": 60},
                },
            ],
        }
    )


def _weekly_yield_summary() -> MeshWorkflowDefinition:
    return MeshWorkflowDefinition.model_validate(
        {
            "name": "Copilot Weekly Yield Summary",
            "description": "Monday morning harvest + yield analytics.",
            "enabled": True,
            "trigger": {"type": "schedule", "filter": {"schedule_cron": "0 7 * * 1"}},
            "actions": [
                {
                    "id": "yield_report",
                    "type": "notification",
                    "channels": ["email"],
                    "template": "Weekly yield summary for owner — panen + analytics.",
                },
                {
                    "id": "log_yield",
                    "type": "log_event",
                    "log_message": "Weekly yield summary dispatched.",
                },
            ],
        }
    )


def workflow_for_prompt(prompt: str) -> MeshWorkflowDefinition:
    normalized = prompt.strip().lower()
    if "moisture" in normalized or "irigasi" in normalized:
        return _irrigation_low_moisture()
    if "hama" in normalized or "drone" in normalized:
        return _pest_drone_response()
    if "pagi" in normalized or "jam 6" in normalized or "summary" in normalized and "farm" in normalized:
        return _morning_farm_summary()
    if "cctv" in normalized or "malam" in normalized or "motion" in normalized:
        return _cctv_night_alarm()
    if "weekly" in normalized or "panen" in normalized or "yield" in normalized:
        return _weekly_yield_summary()
    return _irrigation_low_moisture()


def list_examples() -> list[JsonObject]:
    rows: list[JsonObject] = []
    for prompt in EXAMPLE_PROMPTS:
        wf = workflow_for_prompt(prompt)
        rows.append(
            {
                "prompt": prompt,
                "workflow": wf.model_dump(mode="json"),
            }
        )
    return rows
