"""Super-admin agriculture platform analytics."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import func, select

from app.agriculture.models import AgriFarm, AgriSensorDevice
from app.auth.dependencies import RequireSuperAdmin
from app.deps import DbSession

router = APIRouter(prefix="/agriculture", tags=["super-admin-agriculture"])


@router.get("/stats")
async def platform_agri_stats(user: RequireSuperAdmin, db: DbSession) -> dict[str, object]:
    farms = int(await db.scalar(select(func.count()).select_from(AgriFarm)) or 0)
    hectares = float(await db.scalar(select(func.coalesce(func.sum(AgriFarm.area_hectares), 0))) or 0)
    sensors = int(await db.scalar(select(func.count()).select_from(AgriSensorDevice)) or 0)
    crop_rows = await db.execute(
        select(AgriFarm.crop_type, func.count()).group_by(AgriFarm.crop_type).order_by(func.count().desc())
    )
    top_crops = [{"crop_type": row[0], "count": row[1]} for row in crop_rows.all()]
    return {
        "total_farms": farms,
        "total_hectares": hectares,
        "total_agri_sensors": sensors,
        "top_crops": top_crops,
    }


@router.get("/firmware-fleet")
async def firmware_fleet(user: RequireSuperAdmin, db: DbSession) -> list[dict[str, object]]:
    rows = await db.scalars(select(AgriSensorDevice).limit(500))
    return [
        {
            "sensor_id": str(s.id),
            "lora_dev_eui": s.lora_dev_eui,
            "firmware_version": s.firmware_version,
            "sensor_type": s.sensor_type,
        }
        for s in rows.all()
    ]
