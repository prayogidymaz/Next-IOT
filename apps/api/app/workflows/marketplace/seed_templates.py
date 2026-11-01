"""Pre-seeded marketplace workflow templates."""

from __future__ import annotations

import uuid
from typing import TypedDict

from app.types.json_types import JsonObject


class SeedTemplateSpec(TypedDict):
    name: str
    description: str
    category: str
    tags: list[str]
    snapshot_json: JsonObject


def _base_snapshot(trigger_type: str, action_type: str, action_id: str) -> JsonObject:
    return {
        "name": "seed",
        "enabled": True,
        "definition": {
            "trigger": {"type": trigger_type, "id": "trigger"},
            "conditions": [],
            "actions": [
                {
                    "id": action_id,
                    "type": action_type,
                    "duration_minutes": 15,
                    "log_message": "marketplace-seed-action",
                }
            ],
        },
    }


PRESEEDED_TEMPLATES: list[SeedTemplateSpec] = [
    {
        "name": "Smart Irrigation Kopi",
        "description": "Otomatis siram kopi saat kelembaban tanah di bawah ambang.",
        "category": "irrigation",
        "tags": ["kopi", "soil_moisture", "valve"],
        "snapshot_json": _base_snapshot("sensor_threshold", "set_actuator", "irrigate_valve"),
    },
    {
        "name": "Pest Alert Spodoptera",
        "description": "Trigger pest response saat vision mendeteksi spodoptera.",
        "category": "pest",
        "tags": ["spodoptera", "vision", "sprayer"],
        "snapshot_json": _base_snapshot("event", "dispatch_device", "spray_pest"),
    },
    {
        "name": "Greenhouse Climate Control",
        "description": "Atur kipas dan heater berdasarkan suhu greenhouse.",
        "category": "greenhouse",
        "tags": ["temperature", "hvac"],
        "snapshot_json": _base_snapshot("sensor_threshold", "set_actuator", "climate_fan"),
    },
    {
        "name": "Pond Water Quality",
        "description": "Monitor DO/pH kolam dan aktuasi aerator.",
        "category": "aquaponics",
        "tags": ["pond", "aerator"],
        "snapshot_json": _base_snapshot("sensor_threshold", "set_actuator", "aerator_on"),
    },
    {
        "name": "Energy Saver Lampu",
        "description": "Matikan lampu greenhouse saat cahaya cukup.",
        "category": "energy",
        "tags": ["lux", "lighting"],
        "snapshot_json": _base_snapshot("sensor_threshold", "set_actuator", "lights_off"),
    },
    {
        "name": "Daily Report Scheduler",
        "description": "Kirim laporan harian via notification channel.",
        "category": "report",
        "tags": ["cron", "report"],
        "snapshot_json": _base_snapshot("schedule", "notification", "daily_report"),
    },
]


async def main() -> None:
    from sqlalchemy import select

    from app.database import async_session
    from app.models.tenant import Tenant
    from app.workflows.marketplace.models import WorkflowTemplate

    async with async_session() as db:
        tenant = await db.scalar(select(Tenant).order_by(Tenant.created_at.asc()).limit(1))
        if tenant is None:
            print("WARNING: No tenant in database — create a tenant before seeding marketplace templates.")
            return

        rows = seed_template_rows(tenant.id)
        inserted = 0
        for row in rows:
            name = str(row["name"])
            exists = await db.scalar(
                select(WorkflowTemplate.id).where(
                    WorkflowTemplate.author_tenant_id == tenant.id,
                    WorkflowTemplate.name == name,
                )
            )
            if exists is not None:
                continue
            db.add(WorkflowTemplate(**row))
            inserted += 1
        await db.commit()
        print(f"Seeded {inserted} templates (tenant {tenant.id})")


def seed_template_rows(author_tenant_id: uuid.UUID) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for spec in PRESEEDED_TEMPLATES:
        rows.append(
            {
                "id": uuid.uuid4(),
                "name": spec["name"],
                "description": spec["description"],
                "category": spec["category"],
                "tags_json": spec["tags"],
                "author_tenant_id": author_tenant_id,
                "snapshot_json": spec["snapshot_json"],
                "downloads_count": 0,
                "rating_avg": 0.0,
                "rating_count": 0,
                "published": True,
                "locale": "id",
            }
        )
    return rows


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
