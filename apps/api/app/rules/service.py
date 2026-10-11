import uuid

from fastapi import HTTPException, status
from pydantic import JsonValue
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.devices.service import _get_device_for_user
from app.models.rule import Rule, RuleActionType, RuleTriggerType
from app.models.rule_execution_log import RuleExecutionLog
from app.rules.executor import get_rule_executor, notify_executor_reload
from app.rules.schemas import (
    RuleCreateRequest,
    RuleExecutionLogItem,
    RulePutRequest,
    RuleResponse,
    RuleTestRequest,
    RuleTestResponse,
    RuleUpdateRequest,
)


def _json_dict(raw: dict[str, object]) -> dict[str, JsonValue]:
    out: dict[str, JsonValue] = {}
    for key, value in raw.items():
        if isinstance(key, str) and (
            isinstance(value, dict | list | str | int | float | bool) or value is None
        ):
            out[key] = value
    return out


def _json_actions(raw: list[dict[str, object]]) -> list[dict[str, JsonValue]]:
    return [_json_dict(item) for item in raw if isinstance(item, dict)]


def _to_rule_response(rule: Rule) -> RuleResponse:
    return RuleResponse(
        id=rule.id,
        tenant_id=rule.tenant_id,
        device_id=rule.device_id,
        name=rule.name,
        metric=rule.metric,
        operator=rule.operator,
        threshold=rule.threshold,
        action_type=rule.action_type,
        is_active=rule.is_active,
        enabled=rule.enabled,
        trigger_type=rule.trigger_type,
        trigger_config=_json_dict(rule.trigger_config),
        condition_expr=rule.condition_expr,
        actions=_json_actions(rule.actions if isinstance(rule.actions, list) else []),
        last_executed_at=rule.last_executed_at,
        execution_count=rule.execution_count,
        last_error=rule.last_error,
        priority=rule.priority,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )


def _threshold_from_config(trigger_config: dict[str, object]) -> float:
    raw = trigger_config.get("threshold")
    if isinstance(raw, int | float) and not isinstance(raw, bool):
        return float(raw)
    return 0.0


def _legacy_trigger_config(device_id: uuid.UUID, metric: str, operator: str, threshold: float) -> dict[str, object]:
    op_map = {">": "gt", "<": "lt", "==": "eq", ">=": "gte", "<=": "lte"}
    return {
        "device_id": str(device_id),
        "metric_key": metric,
        "operator": op_map.get(operator, operator),
        "threshold": threshold,
    }


async def _get_rule_for_user(db: AsyncSession, rule_id: uuid.UUID, user: CurrentUser) -> Rule:
    query = select(Rule).where(Rule.id == rule_id)
    if not user.is_super_admin:
        query = query.where(Rule.tenant_id == user.tenant_id)

    rule = await db.scalar(query)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule


async def create_rule(db: AsyncSession, user: CurrentUser, payload: RuleCreateRequest) -> RuleResponse:
    if payload.trigger_type is None:
        assert payload.device_id is not None
        assert payload.metric is not None
        assert payload.operator is not None
        assert payload.threshold is not None
        device = await _get_device_for_user(db, payload.device_id, user)
        if device.tenant_id != user.tenant_id and not user.is_super_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Device tenant mismatch")
        trigger_config = _legacy_trigger_config(device.id, payload.metric, payload.operator, payload.threshold)
        rule = Rule(
            tenant_id=device.tenant_id,
            device_id=device.id,
            name=payload.name,
            metric=payload.metric,
            operator=payload.operator,
            threshold=payload.threshold,
            action_type=payload.action_type,
            is_active=payload.is_active,
            enabled=payload.enabled and payload.is_active,
            trigger_type=RuleTriggerType.TELEMETRY,
            trigger_config=trigger_config,
            actions=[],
        )
    else:
        device_id = payload.device_id
        tenant_id = user.tenant_id
        if device_id is not None:
            device = await _get_device_for_user(db, device_id, user)
            tenant_id = device.tenant_id
        trigger_config = dict(payload.trigger_config or {})
        cfg_device = trigger_config.get("device_id")
        if isinstance(cfg_device, str) and device_id is None:
            try:
                device_id = uuid.UUID(cfg_device)
                await _get_device_for_user(db, device_id, user)
            except ValueError:
                pass
        rule = Rule(
            tenant_id=tenant_id,
            device_id=device_id,
            name=payload.name,
            metric=str(trigger_config.get("metric_key", "metric")),
            operator=">",
            threshold=_threshold_from_config(trigger_config),
            action_type=RuleActionType.ALERT if not payload.actions else "composite",
            is_active=payload.is_active,
            enabled=payload.enabled,
            trigger_type=payload.trigger_type,
            trigger_config=trigger_config,
            condition_expr=payload.condition_expr,
            actions=[{"type": a.type, "config": a.config} for a in (payload.actions or [])],
            priority=payload.priority,
        )

    db.add(rule)
    await db.flush()
    await notify_executor_reload()
    return _to_rule_response(rule)


async def list_rules(
    db: AsyncSession,
    user: CurrentUser,
    *,
    device_id: uuid.UUID | None = None,
    enabled: bool | None = None,
    trigger_type: str | None = None,
) -> list[RuleResponse]:
    query = select(Rule)
    if not user.is_super_admin:
        query = query.where(Rule.tenant_id == user.tenant_id)
    if device_id is not None:
        await _get_device_for_user(db, device_id, user)
        query = query.where(Rule.device_id == device_id)
    if enabled is not None:
        query = query.where(Rule.enabled.is_(enabled))
    if trigger_type is not None:
        query = query.where(Rule.trigger_type == trigger_type)

    result = await db.scalars(query.order_by(Rule.priority.asc(), Rule.created_at.desc()))
    return [_to_rule_response(r) for r in result.all()]


async def get_rule(db: AsyncSession, user: CurrentUser, rule_id: uuid.UUID) -> RuleResponse:
    rule = await _get_rule_for_user(db, rule_id, user)
    return _to_rule_response(rule)


async def list_rules_for_device(
    db: AsyncSession, user: CurrentUser, device_id: uuid.UUID
) -> list[RuleResponse]:
    return await list_rules(db, user, device_id=device_id)


async def update_rule(
    db: AsyncSession, user: CurrentUser, rule_id: uuid.UUID, payload: RuleUpdateRequest
) -> RuleResponse:
    rule = await _get_rule_for_user(db, rule_id, user)

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    if "actions" in updates and updates["actions"] is not None:
        updates["actions"] = [{"type": a["type"], "config": a["config"]} for a in updates["actions"]]

    for field, value in updates.items():
        setattr(rule, field, value)
    if payload.enabled is not None:
        rule.is_active = payload.enabled
    elif payload.is_active is not None:
        rule.enabled = payload.is_active

    await notify_executor_reload()
    return _to_rule_response(rule)


async def put_rule(
    db: AsyncSession, user: CurrentUser, rule_id: uuid.UUID, payload: RulePutRequest
) -> RuleResponse:
    rule = await _get_rule_for_user(db, rule_id, user)
    rule.name = payload.name
    rule.trigger_type = payload.trigger_type
    rule.trigger_config = dict(payload.trigger_config)
    rule.condition_expr = payload.condition_expr
    rule.actions = [{"type": a.type, "config": a.config} for a in payload.actions]
    rule.enabled = payload.enabled
    rule.is_active = payload.enabled
    rule.priority = payload.priority
    rule.device_id = payload.device_id
    await notify_executor_reload()
    return _to_rule_response(rule)


async def delete_rule(db: AsyncSession, user: CurrentUser, rule_id: uuid.UUID) -> None:
    rule = await _get_rule_for_user(db, rule_id, user)
    await db.execute(delete(Rule).where(Rule.id == rule.id))
    await notify_executor_reload()


async def set_rule_enabled(
    db: AsyncSession, user: CurrentUser, rule_id: uuid.UUID, *, enabled: bool
) -> RuleResponse:
    rule = await _get_rule_for_user(db, rule_id, user)
    rule.enabled = enabled
    rule.is_active = enabled
    await notify_executor_reload()
    return _to_rule_response(rule)


async def execute_rule_manual(db: AsyncSession, user: CurrentUser, rule_id: uuid.UUID) -> None:
    rule = await _get_rule_for_user(db, rule_id, user)
    if not rule.enabled:
        return
    executor = get_rule_executor()
    if executor is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Rule executor unavailable")
    await executor.execute_manual(db, rule, None)


async def test_rule(
    db: AsyncSession, user: CurrentUser, rule_id: uuid.UUID, payload: RuleTestRequest
) -> RuleTestResponse:
    rule = await _get_rule_for_user(db, rule_id, user)
    executor = get_rule_executor()
    if executor is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Rule executor unavailable")
    rendered, errors = await executor.dry_run(rule, dict(payload.sample_context))
    return RuleTestResponse(
        rendered_actions=rendered,
        would_execute=len(errors) == 0,
        errors=errors,
    )


async def list_execution_log(
    db: AsyncSession,
    user: CurrentUser,
    rule_id: uuid.UUID,
    *,
    limit: int = 50,
) -> list[RuleExecutionLogItem]:
    await _get_rule_for_user(db, rule_id, user)
    rows = list(
        await db.scalars(
            select(RuleExecutionLog)
            .where(RuleExecutionLog.rule_id == rule_id)
            .order_by(RuleExecutionLog.triggered_at.desc())
            .limit(min(limit, 200))
        )
    )
    return [
        RuleExecutionLogItem(
            id=row.id,
            rule_id=row.rule_id,
            triggered_at=row.triggered_at,
            trigger_context=_json_dict(row.trigger_context),
            status=row.status,
            actions_executed=row.actions_executed,
            error_message=row.error_message,
            duration_ms=row.duration_ms,
        )
        for row in rows
    ]
