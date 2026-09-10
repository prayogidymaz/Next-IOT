import uuid

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rule import Rule, RuleOperator
from app.rules.alerts import emit_alert

OPERATOR_FUNCS = {
    RuleOperator.GT: lambda a, t: a > t,
    RuleOperator.LT: lambda a, t: a < t,
    RuleOperator.EQ: lambda a, t: a == t,
    RuleOperator.GTE: lambda a, t: a >= t,
    RuleOperator.LTE: lambda a, t: a <= t,
}


def evaluate_metric(operator: str, actual: float, threshold: float) -> bool:
    func = OPERATOR_FUNCS.get(operator)
    if func is None:
        return False
    return func(actual, threshold)


async def evaluate_rules_for_telemetry(
    db: AsyncSession,
    redis: aioredis.Redis,
    *,
    device_id: uuid.UUID,
    tenant_id: uuid.UUID,
    metrics: dict[str, float],
    reading_id: uuid.UUID,
) -> int:
    result = await db.scalars(
        select(Rule).where(
            Rule.device_id == device_id,
            Rule.tenant_id == tenant_id,
            Rule.is_active.is_(True),
        )
    )
    rules = result.all()
    triggered = 0

    for rule in rules:
        if rule.metric not in metrics:
            continue
        actual = float(metrics[rule.metric])
        if not evaluate_metric(rule.operator, actual, rule.threshold):
            continue

        await emit_alert(
            redis,
            rule_id=str(rule.id),
            device_id=str(device_id),
            tenant_id=str(tenant_id),
            metric=rule.metric,
            operator=rule.operator,
            threshold=rule.threshold,
            actual_value=actual,
            action_type=rule.action_type,
            reading_id=str(reading_id),
        )
        triggered += 1

    return triggered
