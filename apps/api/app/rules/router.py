import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import RequireOperator
from app.deps import get_db
from app.rules import service
from app.rules.schemas import RuleCreateRequest, RuleResponse, RuleUpdateRequest

router = APIRouter(prefix="/api/v1/rules", tags=["rules"])


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
