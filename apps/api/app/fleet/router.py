"""Fleet automation API."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Response
from pydantic import BaseModel, Field

from app.auth.dependencies import RequireAuth
from app.deps import DbSession
from app.fleet import group_manager, provisioning
from app.fleet.config_sync import sync_config_to_group
from app.fleet.models import DeviceConfigTemplate
from app.types.json_types import JsonObject
from sqlalchemy import select

router = APIRouter(prefix="/api/v1/fleet", tags=["fleet"])


class TemplateCreate(BaseModel):
    name: str
    device_type: str
    config_json: dict[str, object] = Field(default_factory=dict)
    firmware_version: str = ""


class TemplateView(BaseModel):
    id: uuid.UUID
    name: str
    device_type: str
    firmware_version: str

    model_config = {"from_attributes": True}


class ProvisionBody(BaseModel):
    template_id: uuid.UUID | None = None
    device_count: int = Field(ge=1, le=500)


class GroupCreate(BaseModel):
    name: str
    tag_filter_json: dict[str, object] = Field(default_factory=dict)


class GroupView(BaseModel):
    id: uuid.UUID
    name: str
    tag_filter_json: dict[str, object]

    model_config = {"from_attributes": True}


@router.get("/templates", response_model=list[TemplateView])
async def list_templates(user: RequireAuth, db: DbSession) -> list[TemplateView]:
    rows = await db.scalars(select(DeviceConfigTemplate).where(DeviceConfigTemplate.tenant_id == user.tenant_id))
    return [TemplateView.model_validate(r) for r in rows.all()]


@router.post("/templates", response_model=TemplateView, status_code=201)
async def create_template(user: RequireAuth, db: DbSession, payload: TemplateCreate) -> TemplateView:
    row = DeviceConfigTemplate(
        tenant_id=user.tenant_id,
        name=payload.name,
        device_type=payload.device_type,
        config_json=payload.config_json,
        firmware_version=payload.firmware_version,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return TemplateView.model_validate(row)


@router.post("/provision", status_code=201)
async def bulk_provision(user: RequireAuth, db: DbSession, payload: ProvisionBody) -> dict[str, str]:
    job = await provisioning.start_bulk_job(db, user, payload.template_id, payload.device_count)
    return {"job_id": str(job.id), "status": job.status}


@router.get("/provision/{job_id}/csv")
async def download_provision_csv(user: RequireAuth, db: DbSession, job_id: uuid.UUID) -> Response:
    from app.fleet.models import BulkProvisioningJob

    job = await db.get(BulkProvisioningJob, job_id)
    if job is None or job.tenant_id != user.tenant_id:
        return Response(status_code=404)
    template = await db.get(DeviceConfigTemplate, job.template_id) if job.template_id else None
    data = provisioning.export_tokens_csv(job, template)
    return Response(content=data, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=provision-{job_id}.csv"})


@router.get("/groups", response_model=list[GroupView])
async def list_device_groups(user: RequireAuth, db: DbSession) -> list[GroupView]:
    rows = await group_manager.list_groups(db, user)
    return [GroupView.model_validate(r) for r in rows]


@router.post("/groups", response_model=GroupView, status_code=201)
async def create_device_group(user: RequireAuth, db: DbSession, payload: GroupCreate) -> GroupView:
    row = await group_manager.create_group(db, user, payload.name, payload.tag_filter_json)
    return GroupView.model_validate(row)


@router.post("/groups/{group_id}/sync")
async def sync_group_config(user: RequireAuth, db: DbSession, group_id: uuid.UUID, body: JsonObject) -> dict[str, int | float]:
    await group_manager.get_group(db, user, group_id)
    return await sync_config_to_group(db, user, group_id, body, None)
