"""Seed four cross-domain mesh workflow presets for demo tenants."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mesh.workflow_schema import MeshWorkflowDefinition
from app.models.mesh_workflow import MeshWorkflow
from app.models.tenant import Tenant

PRESET_KEYS = (
    "smart_irrigation_extended",
    "farm_pest_response",
    "security_patrol_night",
    "harvest_coordination",
)


def _presets() -> list[MeshWorkflowDefinition]:
    return [
        MeshWorkflowDefinition.model_validate(
            {
                "name": "Smart Irrigation Extended",
                "description": "Open valve when soil moisture low and no rain forecast.",
                "enabled": True,
                "trigger": {
                    "type": "mesh_event",
                    "filter": {
                        "domain": "sensor",
                        "event_type": "threshold_exceeded",
                        "payload_match": {"metric": "moisture", "operator": "lt", "threshold": 40},
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
                        "id": "open_valve",
                        "type": "trigger_device",
                        "device_resolver": {"capability": "can_control_valve"},
                        "command": "open_valve",
                        "params": {"duration_minutes": 15},
                    },
                    {
                        "id": "notify",
                        "type": "notification",
                        "channels": ["whatsapp"],
                        "template": "Irrigation started for plot {{trigger.context.physical_zone}}.",
                    },
                ],
            }
        ),
        MeshWorkflowDefinition.model_validate(
            {
                "name": "Farm Pest Response",
                "description": "Dispatch drone on vision motion, capture NDVI, notify team.",
                "enabled": True,
                "trigger": {
                    "type": "mesh_event",
                    "filter": {
                        "domain": "vision",
                        "event_type": "motion_detected",
                        "payload_match": {"confidence": {"$gte": 0.75}},
                    },
                },
                "conditions": [
                    {
                        "type": "device_state",
                        "device_resolver": {
                            "capability": "can_fly_to",
                            "nearest_to": "{{trigger.context.geo_location}}",
                        },
                        "state_match": {"status": "online", "battery": {"$gte": 50}},
                    }
                ],
                "actions": [
                    {
                        "id": "action_1",
                        "type": "dispatch_device",
                        "device_resolver": {
                            "capability": "can_fly_to",
                            "nearest_to": "{{trigger.context.geo_location}}",
                        },
                        "command": "fly_to",
                        "params": {"target": "{{trigger.context.geo_location}}", "altitude": 20},
                    },
                    {
                        "id": "action_3",
                        "type": "trigger_device",
                        "device_resolver": {
                            "capability": "can_capture_ndvi",
                            "device_id": "{{action_1.resolved_device_id}}",
                        },
                        "command": "capture_ndvi",
                        "params": {},
                    },
                    {
                        "id": "action_4",
                        "type": "notification",
                        "channels": ["whatsapp"],
                        "template": (
                            "Pest detected plot {{trigger.context.physical_zone}}, "
                            "drone dispatched + NDVI captured."
                        ),
                    },
                ],
            }
        ),
        MeshWorkflowDefinition.model_validate(
            {
                "name": "Security Patrol Night",
                "description": "Night intrusion: lock gates, record CCTV, dispatch drone, WA alert.",
                "enabled": True,
                "trigger": {
                    "type": "mesh_event",
                    "filter": {
                        "domain": "security",
                        "event_type": "intrusion_detected",
                        "time_filter": {"start": "22:00", "end": "06:00"},
                    },
                },
                "actions": [
                    {
                        "id": "lock_gates",
                        "type": "trigger_device",
                        "device_resolver": {"capability": "can_lock"},
                        "command": "lock",
                        "params": {},
                    },
                    {
                        "id": "cctv_record",
                        "type": "trigger_device",
                        "device_resolver": {"capability": "can_capture_video"},
                        "command": "record",
                        "params": {"duration_seconds": 60},
                    },
                    {
                        "id": "drone_patrol",
                        "type": "dispatch_device",
                        "device_resolver": {"capability": "can_fly_to"},
                        "command": "fly_to",
                        "params": {"target": "{{trigger.context.geo_location}}"},
                    },
                    {
                        "id": "notify_security",
                        "type": "notification",
                        "channels": ["whatsapp"],
                        "template": "Security patrol triggered for zone {{trigger.context.physical_zone}}.",
                    },
                ],
            }
        ),
        MeshWorkflowDefinition.model_validate(
            {
                "name": "Harvest Coordination",
                "description": "Daily harvest survey workflow (schedule trigger; manual execute supported).",
                "enabled": True,
                "trigger": {
                    "type": "schedule",
                    "filter": {"schedule_cron": "0 6 * * *"},
                },
                "conditions": [
                    {
                        "type": "attribute_true",
                        "device_resolver": {"capability": "can_fly_to"},
                        "attribute": "harvest_window_open",
                    }
                ],
                "actions": [
                    {
                        "id": "yield_survey",
                        "type": "dispatch_device",
                        "device_resolver": {"capability": "can_fly_to"},
                        "command": "fly_to",
                        "params": {},
                    },
                    {
                        "id": "capture_plot",
                        "type": "trigger_device",
                        "device_resolver": {"capability": "can_capture_image"},
                        "command": "capture_image",
                        "params": {},
                    },
                    {
                        "id": "log_yield",
                        "type": "log_event",
                        "log_message": "Yield survey logged for {{trigger.context.physical_zone}}",
                    },
                    {
                        "id": "notify_harvest",
                        "type": "notification",
                        "channels": ["whatsapp"],
                        "template": "Tim panen: survey drone selesai untuk {{trigger.context.physical_zone}}.",
                    },
                ],
            }
        ),
    ]


async def seed_mesh_preset_workflows(db: AsyncSession, tenant_slug: str) -> int:
    tenant = await db.scalar(select(Tenant).where(Tenant.slug == tenant_slug))
    if tenant is None:
        return 0
    created = 0
    presets = _presets()
    for index, definition in enumerate(presets):
        key = PRESET_KEYS[index]
        existing = await db.scalar(
            select(MeshWorkflow).where(
                MeshWorkflow.tenant_id == tenant.id,
                MeshWorkflow.name == definition.name,
            )
        )
        if existing is not None:
            continue
        row = MeshWorkflow(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            name=definition.name,
            description=definition.description,
            enabled=definition.enabled,
            definition={
                "preset_key": key,
                "trigger": definition.trigger.model_dump(mode="json"),
                "conditions": [item.model_dump(mode="json") for item in definition.conditions],
                "actions": [item.model_dump(mode="json") for item in definition.actions],
            },
        )
        db.add(row)
        created += 1
    await db.flush()
    return created
