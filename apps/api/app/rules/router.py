import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import RequireAutomationManage, RequireAutomationRun, RequireOperator
from app.deps import get_db
from app.rules import service
from app.rules.pipeline_io import export_pipeline_rule, import_pipeline_rule, validate_pipeline_payload
from app.rules.schemas import (
    PipelineExportResponse,
    PipelineImportRequest,
    PipelineValidateRequest,
    PipelineValidateResponse,
    RuleCreateRequest,
    RuleResponse,
    RuleUpdateRequest,
)

router = APIRouter(prefix="/api/v1/rules", tags=["rules"])


@router.post("/import", response_model=PipelineExportResponse, status_code=status.HTTP_201_CREATED)
async def import_pipeline_json(
    payload: PipelineImportRequest,
    user: RequireAutomationManage,
    db: AsyncSession = Depends(get_db),
):
    document = await import_pipeline_rule(db, user, payload.document)
    return PipelineExportResponse.model_validate(document)


@router.post("/validate", response_model=PipelineValidateResponse)
async def validate_pipeline_json(
    payload: PipelineValidateRequest,
    user: RequireAutomationRun,
):
    result = validate_pipeline_payload(payload.document)
    return PipelineValidateResponse.model_validate(result)


@router.get("/{rule_id}/export", response_model=PipelineExportResponse)
async def export_pipeline_json(
    rule_id: uuid.UUID,
    user: RequireAutomationRun,
    db: AsyncSession = Depends(get_db),
):
    document = await export_pipeline_rule(db, user, rule_id)
    return PipelineExportResponse.model_validate(document)


@router.get("", response_model=list[RuleResponse])
async def list_rules(
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
    device_id: uuid.UUID | None = None,
):
    return await service.list_rules(db, user, device_id=device_id)


@router.post("", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    payload: RuleCreateRequest,
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
):
    return await service.create_rule(db, user, payload)


@router.patch("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: uuid.UUID,
    payload: RuleUpdateRequest,
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
):
    return await service.update_rule(db, user, rule_id, payload)


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: uuid.UUID,
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
):
    await service.delete_rule(db, user, rule_id)
