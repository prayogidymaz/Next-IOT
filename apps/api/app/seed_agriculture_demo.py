"""Agriculture demo seeder implementation."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select

from app.agriculture.crypto import encrypt_app_key
from app.agriculture.models import (
    AgriDiseaseAlert,
    AgriFarm,
    AgriIrrigationValve,
    AgriLoraGateway,
    AgriPlot,
    AgriSensorDevice,
)
from app.database import async_session
from app.models.partner import Partner  # noqa: F401 — register partners for Tenant FK
from app.models.tenant import Tenant


async def main() -> None:
    async with async_session() as db:
        tenant = await db.scalar(select(Tenant).where(Tenant.slug == "kopi-toraja-mitra"))
        if tenant is None:
            tenant = Tenant(name="Kopi Toraja Mitra Tani", slug="kopi-toraja-mitra", security_tier="pro")
            db.add(tenant)
            await db.flush()
        farm = await db.scalar(
            select(AgriFarm).where(AgriFarm.tenant_id == tenant.id, AgriFarm.name == "Kebun Utama")
        )
        if farm is None:
            farm = AgriFarm(
                tenant_id=tenant.id,
                name="Kebun Utama",
                crop_type="coffee",
                area_hectares=Decimal("5"),
                location_lat=Decimal("-3.0738"),
                location_lng=Decimal("119.8707"),
                location_address="Toraja",
                owner_whatsapp="6281234567890",
            )
            db.add(farm)
            await db.flush()
        plots = list((await db.scalars(select(AgriPlot).where(AgriPlot.farm_id == farm.id))).all())
        if not plots:
            for name in ("Blok A", "Blok B", "Blok C"):
                p = AgriPlot(farm_id=farm.id, name=name, area_hectares=Decimal("1.5"))
                db.add(p)
                plots.append(p)
            await db.flush()
        gw_count = int(
            await db.scalar(
                select(func.count()).select_from(AgriLoraGateway).where(AgriLoraGateway.farm_id == farm.id)
            )
            or 0
        )
        if gw_count == 0:
            db.add(
                AgriLoraGateway(
                    tenant_id=tenant.id,
                    farm_id=farm.id,
                    name="Gateway Utama",
                    gateway_eui="GWDEADBEEF000001",
                    status="online",
                    last_seen_at=datetime.now(tz=UTC),
                )
            )
        sensor_count = int(
            await db.scalar(
                select(func.count()).select_from(AgriSensorDevice).where(AgriSensorDevice.farm_id == farm.id)
            )
            or 0
        )
        if sensor_count == 0:
            for i, plot in enumerate(plots):
                for j in range(3 if i == 0 else 2):
                    eui = f"S{i}{j}{uuid.uuid4().hex[:10]}".upper()[:16]
                    db.add(
                        AgriSensorDevice(
                            tenant_id=tenant.id,
                            farm_id=farm.id,
                            plot_id=plot.id,
                            name=f"Soil {i}-{j}",
                            sensor_type="soil_moisture",
                            lora_dev_eui=eui,
                            lora_app_key_enc=encrypt_app_key("00112233445566778899AABBCCDDEEFF"),
                            last_battery_voltage=Decimal("3.70"),
                        )
                    )
        for plot in plots:
            valve_n = int(
                await db.scalar(
                    select(func.count())
                    .select_from(AgriIrrigationValve)
                    .where(AgriIrrigationValve.plot_id == plot.id)
                )
                or 0
            )
            if valve_n == 0:
                db.add(
                    AgriIrrigationValve(
                        farm_id=farm.id,
                        plot_id=plot.id,
                        name=f"Valve {plot.name}",
                        flow_rate_lpm=Decimal("25"),
                    )
                )
        if plots:
            alert_n = int(
                await db.scalar(
                    select(func.count())
                    .select_from(AgriDiseaseAlert)
                    .where(AgriDiseaseAlert.plot_id == plots[0].id)
                )
                or 0
            )
            if alert_n == 0:
                db.add(
                    AgriDiseaseAlert(
                        plot_id=plots[0].id,
                        disease_name="Karat Daun Kopi",
                        risk_level="high",
                        factors={"humidity_pct": 88},
                        action_recommended="Semprot fungisida",
                    )
                )
        await db.commit()
        print("Agriculture demo seed complete for tenant", tenant.slug)
