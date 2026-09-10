import uuid

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.devices.service import _get_device_for_user
from app.models.rule import Rule
from app.rules.schemas import RuleCreateRequest, RuleResponse, RuleUpdateRequest


def _to_rule_response(rule: Rule) -> RuleResponse:
    return RuleResponse.model_validate(rule)


async def _get_rule_for_user(db: AsyncSession, rule_id: uuid.UUID, user: CurrentUser) -> Rule:
    query = select(Rule).where(Rule.id == rule_id)
    if not user.is_super_admin:
        query = query.where(Rule.tenant_id == user.tenant_id)

    rule = await db.scalar(query)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule


async def create_rule(db: AsyncSession, user: CurrentUser, payload: RuleCreateRequest) -> RuleResponse:
    device = await _get_device_for_user(db, payload.device_id, user)
    if device.tenant_id != user.tenant_id and not user.is_super_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Device tenant mismatch")

    rule = Rule(
        tenant_id=device.tenant_id,
        device_id=device.id,
        name=payload.name,
        metric=payload.metric,
        operator=payload.operator,
        threshold=payload.threshold,
        action_type=payload.action_type,
        is_active=payload.is_active,
    )
    db.add(rule)
    await db.flush()
    return _to_rule_response(rule)


async def list_rules(
    db: AsyncSession,
    user: CurrentUser,
    *,
    device_id: uuid.UUID | None = None,
) -> list[RuleResponse]:
    query = select(Rule)
    if not user.is_super_admin:
        query = query.where(Rule.tenant_id == user.tenant_id)
    if device_id is not None:
        await _get_device_for_user(db, device_id, user)
        query = query.where(Rule.device_id == device_id)

    result = await db.scalars(query.order_by(Rule.created_at.desc()))
    return [_to_rule_response(r) for r in result.all()]


async def list_rules_for_device(
    db: AsyncSession, user: CurrentUser, device_id: uuid.UUID
) -> list[RuleResponse]:
    await _get_device_for_user(db, device_id, user)

    query = select(Rule).where(Rule.device_id == device_id)
    if not user.is_super_admin:
        query = query.where(Rule.tenant_id == user.tenant_id)

    result = await db.scalars(query.order_by(Rule.created_at.desc()))
    return [_to_rule_response(r) for r in result.all()]


async def update_rule(
    db: AsyncSession, user: CurrentUser, rule_id: uuid.UUID, payload: RuleUpdateRequest
) -> RuleResponse:
    rule = await _get_rule_for_user(db, rule_id, user)

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    for field, value in updates.items():
        setattr(rule, field, value)

    return _to_rule_response(rule)


async def delete_rule(db: AsyncSession, user: CurrentUser, rule_id: uuid.UUID) -> None:
    rule = await _get_rule_for_user(db, rule_id, user)
    await db.execute(delete(Rule).where(Rule.id == rule.id))
