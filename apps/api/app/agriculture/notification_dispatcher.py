"""WhatsApp notifications for agriculture vertical (Fonnte)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agriculture.models import (
    AgriDiseaseAlert,
    AgriFarm,
    AgriIrrigationValve,
    AgriPlot,
    AgriSensorDevice,
)
from app.config import settings
from app.notifications.providers.fonnte import FonnteProvider
from app.types.json_types import JsonObject
from app.types.redis_client import RedisClient

_TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "notifications" / "templates" / "agriculture"
_jinja = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=select_autoescape(enabled_extensions=()),
)


def _default_settings() -> dict[str, object]:
    return {
        "disease_alerts": True,
        "irrigation": True,
        "battery": True,
        "weather": True,
        "harvest": True,
        "whatsapp_number": "",
    }


def farm_notification_settings(farm: AgriFarm) -> dict[str, object]:
    raw = farm.metadata_json.get("notification_settings")
    if isinstance(raw, dict):
        merged = _default_settings()
        merged.update(raw)
        return merged
    return _default_settings()


def _phone_for_farm(farm: AgriFarm, settings_map: dict[str, object]) -> str:
    wa = settings_map.get("whatsapp_number")
    if isinstance(wa, str) and wa.strip():
        return wa.strip()
    return farm.owner_whatsapp.strip()


def _render(template_name: str, variables: dict[str, object]) -> str:
    template = _jinja.get_template(template_name)
    return template.render(**variables).strip()


class AgriNotificationDispatcher:
    def __init__(self, db: AsyncSession, redis: RedisClient) -> None:
        self._db = db
        self._redis = redis
        self._provider = FonnteProvider()

    async def _send(
        self,
        farm: AgriFarm,
        title: str,
        body: str,
        severity: str,
        redis_dedup_key: str | None,
        dedup_ttl_seconds: int,
    ) -> bool:
        prefs = farm_notification_settings(farm)
        phone = _phone_for_farm(farm, prefs)
        if not phone:
            return False
        if redis_dedup_key:
            if int(await self._redis.exists(redis_dedup_key)) > 0:
                return False
        config: JsonObject = {"phone_number": phone, "api_token": settings.notification_fonnte_default_token}
        result = await self._provider.send(config, title, body, severity)
        if result.success and redis_dedup_key:
            await self._redis.setex(redis_dedup_key, dedup_ttl_seconds, "1")
        return result.success

    async def send_disease_alert(self, alert_id: uuid.UUID) -> bool:
        alert = await self._db.scalar(select(AgriDiseaseAlert).where(AgriDiseaseAlert.id == alert_id))
        if alert is None:
            return False
        if alert.notified_at is not None:
            return False
        if alert.snoozed_until and alert.snoozed_until > datetime.now(tz=UTC):
            return False
        plot = await self._db.scalar(select(AgriPlot).where(AgriPlot.id == alert.plot_id))
        if plot is None:
            return False
        farm = await self._db.scalar(select(AgriFarm).where(AgriFarm.id == plot.farm_id))
        if farm is None:
            return False
        prefs = farm_notification_settings(farm)
        if not prefs.get("disease_alerts", True):
            return False
        if alert.risk_level not in ("high", "critical", "medium"):
            return False
        template = "disease_alert_high.jinja2"
        factors_lines = "\n".join(f"- {k}: {v}" for k, v in alert.factors.items())
        body = _render(
            template,
            {
                "farm_name": farm.name,
                "disease_name": alert.disease_name,
                "factors": factors_lines,
                "action": alert.action_recommended,
                "link": f"/agriculture/farms/{farm.id}/alerts",
            },
        )
        ok = await self._send(
            farm,
            f"Peringatan {alert.disease_name}",
            body,
            alert.risk_level,
            f"agri:wa:disease:{alert.id}",
            3600,
        )
        if ok:
            alert.notified_at = datetime.now(tz=UTC)
            await self._db.commit()
        return ok

    async def send_irrigation_notification(self, action: str, valve_id: uuid.UUID) -> bool:
        valve = await self._db.scalar(select(AgriIrrigationValve).where(AgriIrrigationValve.id == valve_id))
        if valve is None:
            return False
        farm = await self._db.scalar(select(AgriFarm).where(AgriFarm.id == valve.farm_id))
        plot = await self._db.scalar(select(AgriPlot).where(AgriPlot.id == valve.plot_id))
        if farm is None:
            return False
        prefs = farm_notification_settings(farm)
        if not prefs.get("irrigation", True):
            return False
        template = "irrigation_started.jinja2" if action == "started" else "irrigation_completed.jinja2"
        body = _render(
            template,
            {
                "farm_name": farm.name,
                "valve_name": valve.name,
                "plot_name": plot.name if plot else "",
                "duration_minutes": "",
                "volume_liters": "",
                "next_scheduled": "",
            },
        )
        dedup = f"agri:wa:irrigation:{valve_id}:{action}"
        return await self._send(farm, f"Irigasi {action}", body, "info", dedup, 300)

    async def send_low_battery_warning(self, sensor_id: uuid.UUID) -> bool:
        sensor = await self._db.scalar(select(AgriSensorDevice).where(AgriSensorDevice.id == sensor_id))
        if sensor is None:
            return False
        farm = await self._db.scalar(select(AgriFarm).where(AgriFarm.id == sensor.farm_id))
        if farm is None:
            return False
        prefs = farm_notification_settings(farm)
        if not prefs.get("battery", True):
            return False
        voltage = float(sensor.last_battery_voltage or 0)
        body = _render(
            "low_battery.jinja2",
            {
                "sensor_name": sensor.name or sensor.lora_dev_eui,
                "voltage": f"{voltage:.2f}",
                "days_remaining_estimate": "7",
                "replacement_guide_link": "/agriculture",
            },
        )
        return await self._send(
            farm,
            "Baterai sensor lemah",
            body,
            "warning",
            f"agri:wa:battery:{sensor_id}",
            7 * 24 * 3600,
        )

    async def send_sensor_offline(self, sensor_id: uuid.UUID) -> bool:
        sensor = await self._db.scalar(select(AgriSensorDevice).where(AgriSensorDevice.id == sensor_id))
        if sensor is None or sensor.farm_id is None:
            return False
        farm = await self._db.scalar(select(AgriFarm).where(AgriFarm.id == sensor.farm_id))
        if farm is None:
            return False
        body = _render(
            "sensor_offline.jinja2",
            {"sensor_name": sensor.name, "since": datetime.now(tz=UTC).isoformat()},
        )
        return await self._send(
            farm,
            "Sensor offline",
            body,
            "warning",
            f"agri:wa:offline:{sensor_id}",
            24 * 3600,
        )

    async def send_weather_warning(self, farm_id: uuid.UUID, forecast_label: str) -> bool:
        farm = await self._db.scalar(select(AgriFarm).where(AgriFarm.id == farm_id))
        if farm is None:
            return False
        prefs = farm_notification_settings(farm)
        if not prefs.get("weather", True):
            return False
        body = _render(
            "weather_warning.jinja2",
            {
                "farm_name": farm.name,
                "weather_type": forecast_label,
                "timing": "24 jam",
                "recommendations": "Tunda irigasi dan amankan hasil panen.",
            },
        )
        return await self._send(
            farm,
            "Peringatan cuaca",
            body,
            "warning",
            f"agri:wa:weather:{farm_id}",
            3 * 3600,
        )

    async def send_harvest_reminder(self, farm_id: uuid.UUID, predicted_date: str) -> bool:
        farm = await self._db.scalar(select(AgriFarm).where(AgriFarm.id == farm_id))
        if farm is None:
            return False
        prefs = farm_notification_settings(farm)
        if not prefs.get("harvest", True):
            return False
        body = _render(
            "harvest_time.jinja2",
            {
                "farm_name": farm.name,
                "date": predicted_date,
                "quality_prediction": "Baik",
                "buyer_contacts": "",
            },
        )
        return await self._send(
            farm,
            "Waktu panen mendekat",
            body,
            "info",
            f"agri:wa:harvest:{farm_id}",
            24 * 3600,
        )

    async def send_custom_message(self, farm_id: uuid.UUID, title: str, body: str) -> bool:
        farm = await self._db.scalar(select(AgriFarm).where(AgriFarm.id == farm_id))
        if farm is None:
            return False
        return await self._send(farm, title, body, "info", None, 0)

    async def send_test(self, farm_id: uuid.UUID) -> bool:
        farm = await self._db.scalar(select(AgriFarm).where(AgriFarm.id == farm_id))
        if farm is None:
            return False
        return await self._send(
            farm,
            "Tes notifikasi Next-IoT Agri",
            "Pesan uji dari Smart Agriculture. Fonnte terhubung.",
            "info",
            None,
            0,
        )
