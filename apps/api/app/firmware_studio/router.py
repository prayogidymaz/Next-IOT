"""Firmware Studio API."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import PlainTextResponse, Response

from app.auth.dependencies import RequireOperator
from app.deps import DbSession
from app.firmware_studio import generator
from app.firmware_studio.schemas import (
    FirmwareGenerateRequest,
    FirmwarePreviewResponse,
    FirmwareTemplateInfo,
    FrameworkTarget,
    McuTarget,
)
from app.firmware_studio.sensor_drivers import catalog_public

router = APIRouter(prefix="/api/v1/firmware-studio", tags=["firmware-studio"])


@router.get("/sensor-drivers")
async def list_sensor_drivers(_user: RequireOperator) -> dict[str, list[str]]:
    return catalog_public()


_AGRI_TEMPLATES = (
    "agri_soil_sensor.cpp",
    "agri_weather_station.cpp",
    "agri_irrigation_controller.cpp",
    "agri_npk_sensor.cpp",
)


@router.get("/agri-templates")
async def list_agri_templates(_user: RequireOperator) -> list[str]:
    return list(_AGRI_TEMPLATES)


@router.get("/agri-templates/{name}")
async def get_agri_template(name: str, _user: RequireOperator) -> PlainTextResponse:
    if name not in _AGRI_TEMPLATES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown template")
    path = Path(__file__).resolve().parent / "templates" / name
    return PlainTextResponse(path.read_text(encoding="utf-8"))


@router.get("/templates", response_model=FirmwareTemplateInfo)
async def list_templates(_user: RequireOperator) -> FirmwareTemplateInfo:
    return FirmwareTemplateInfo(
        mcus=[m.value for m in McuTarget],
        frameworks=[f.value for f in FrameworkTarget],
    )


@router.post("/preview", response_model=FirmwarePreviewResponse)
async def preview_firmware(
    payload: FirmwareGenerateRequest,
    user: RequireOperator,
    db: DbSession,
) -> FirmwarePreviewResponse:
    try:
        return await generator.preview_for_user(db, user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.post("/generate")
async def generate_firmware_zip(
    payload: FirmwareGenerateRequest,
    user: RequireOperator,
    db: DbSession,
) -> Response:
    try:
        zip_bytes, filename = await generator.generate_for_user(db, user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
