import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import RequireOperator, RequireTenantAdmin, RequireViewer
from app.deps import get_db
from app.rules import service
from app.rules.pipeline_io import export_pipeline_rule, import_pipeline_rule, validate_pipeline_payload
from app.rules.schemas import (
    PipelineExportResponse,
    PipelineImportRequest,
    PipelineValidateRequest,
    PipelineValidateResponse,
    RuleCreateRequest,
    RuleExecutionLogItem,
    RulePutRequest,
    RuleResponse,
    RuleTestRequest,
    RuleTestResponse,
    RuleUpdateRequest,
)

router = APIRouter(prefix="/api/v1/rules", tags=["rules"])


@router.post("/import", response_model=PipelineExportResponse, status_code=status.HTTP_201_CREATED)
async def import_pipeline_json(
    payload: PipelineImportRequest,
    user: RequireTenantAdmin,
    db: AsyncSession = Depends(get_db),
):
    document = await import_pipeline_rule(db, user, payload.document)
    return PipelineExportResponse.model_validate(document)


@router.post("/validate", response_model=PipelineValidateResponse)
async def validate_pipeline_json(
    payload: PipelineValidateRequest,
    user: RequireOperator,
):
    result = validate_pipeline_payload(payload.document)
    return PipelineValidateResponse.model_validate(result)


@router.get("/{rule_id}/export", response_model=PipelineExportResponse)
async def export_pipeline_json(
    rule_id: uuid.UUID,
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
):
    document = await export_pipeline_rule(db, user, rule_id)
    return PipelineExportResponse.model_validate(document)


@router.get("", response_model=list[RuleResponse])
async def list_rules(
    user: RequireViewer,
    db: AsyncSession = Depends(get_db),
    device_id: uuid.UUID | None = None,
    enabled: bool | None = None,
    trigger_type: str | None = None,
):
    return await service.list_rules(
        db, user, device_id=device_id, enabled=enabled, trigger_type=trigger_type
    )


@router.post("", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    payload: RuleCreateRequest,
    user: RequireTenantAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await service.create_rule(db, user, payload)


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: uuid.UUID,
    user: RequireViewer,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_rule(db, user, rule_id)


@router.patch("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: uuid.UUID,
    payload: RuleUpdateRequest,
    user: RequireTenantAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await service.update_rule(db, user, rule_id, payload)


@router.put("/{rule_id}", response_model=RuleResponse)
async def put_rule(
    rule_id: uuid.UUID,
    payload: RulePutRequest,
    user: RequireTenantAdmin,
    db: AsyncSession = Depends(get_db),
):
    return await service.put_rule(db, user, rule_id, payload)


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: uuid.UUID,
    user: RequireTenantAdmin,
    db: AsyncSession = Depends(get_db),
):
    await service.delete_rule(db, user, rule_id)


@router.post("/{rule_id}/execute", status_code=status.HTTP_204_NO_CONTENT)
async def execute_rule(
    rule_id: uuid.UUID,
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
):
    await service.execute_rule_manual(db, user, rule_id)


@router.post("/{rule_id}/test", response_model=RuleTestResponse)
async def test_rule(
    rule_id: uuid.UUID,
    payload: RuleTestRequest,
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
):
    return await service.test_rule(db, user, rule_id, payload)


@router.get("/{rule_id}/execution-log", response_model=list[RuleExecutionLogItem])
async def execution_log(
    rule_id: uuid.UUID,
    user: RequireViewer,
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
):
    return await service.list_execution_log(db, user, rule_id, limit=limit)


@router.post("/{rule_id}/enable", response_model=RuleResponse)
async def enable_rule(
    rule_id: uuid.UUID,
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
):
    return await service.set_rule_enabled(db, user, rule_id, enabled=True)


@router.post("/{rule_id}/disable", response_model=RuleResponse)
async def disable_rule(
    rule_id: uuid.UUID,
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
):
    return await service.set_rule_enabled(db, user, rule_id, enabled=False)
