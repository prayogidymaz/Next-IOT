"""Regression: every ForeignKey target table must exist in SQLAlchemy metadata."""

from __future__ import annotations

import app.models as _models_registry
from app.database import Base


def test_models_package_registers_tables() -> None:
    assert _models_registry.Tenant is not None
    assert len(Base.metadata.tables) >= 50


def test_foreign_key_targets_exist_in_metadata() -> None:
    table_names = set(Base.metadata.tables.keys())
    orphans: list[str] = []
    for source_table, table in Base.metadata.tables.items():
        for fk in table.foreign_key_constraints:
            target = fk.referred_table.name
            if target not in table_names:
                orphans.append(f"{source_table} -> {target}")
    assert orphans == [], "Orphan foreign keys (target table missing from metadata):\n" + "\n".join(
        sorted(orphans)
    )


def test_expected_step_tables_registered() -> None:
    required = {
        "partners",
        "tenants",
        "subscription_plans",
        "tenant_subscriptions",
        "invoices",
        "payment_methods",
        "alarms",
        "alarm_history",
        "notification_channels",
        "notification_rules",
        "notification_log",
        "rule_execution_log",
        "platform_email_templates",
        "support_tickets",
        "platform_backups",
        "impersonation_sessions",
        "agri_farms",
        "agri_plots",
        "agri_sensor_devices",
        "agri_disease_alerts",
    }
    registered = set(Base.metadata.tables.keys())
    missing = sorted(required - registered)
    assert missing == [], f"Expected tables not registered: {missing}"
