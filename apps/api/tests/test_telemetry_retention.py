from app.auth.tiering import SecurityTier
from app.config import Settings
from app.telemetry.retention import (
    global_retention_policy_sql,
    retention_days_for_tier,
    tenant_retention_delete_sql,
)


def test_retention_days_for_tier_mapping() -> None:
    settings = Settings()
    assert retention_days_for_tier(SecurityTier.FREE) == settings.telemetry_retention_free_days
    assert retention_days_for_tier(SecurityTier.PRO) == settings.telemetry_retention_pro_days
    assert retention_days_for_tier(SecurityTier.ENTERPRISE) == settings.telemetry_retention_enterprise_days


def test_global_retention_policy_sql_uses_enterprise_days() -> None:
    settings = Settings()
    sql = global_retention_policy_sql(settings.telemetry_retention_enterprise_days)
    assert "add_retention_policy" in sql
    assert f"INTERVAL '{settings.telemetry_retention_enterprise_days} days'" in sql
    assert "if_not_exists => true" in sql


def test_tenant_retention_delete_sql_shape() -> None:
    sql = tenant_retention_delete_sql()
    assert "DELETE FROM telemetry_readings" in sql
    assert "tenant_id = :tenant_id" in sql
    assert "recorded_at < :cutoff" in sql
