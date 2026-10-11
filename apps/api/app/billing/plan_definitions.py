"""Default subscription plan catalog (seed source)."""

from __future__ import annotations

from pydantic import JsonValue


def plan_seed_rows() -> list[dict[str, JsonValue]]:
    return [
        {
            "code": "free",
            "name": "Free",
            "description": "Trial / hobby projects",
            "monthly_price_idr": 0,
            "yearly_price_idr": 0,
            "display_order": 1,
            "limits": {
                "max_devices": 5,
                "max_users": 1,
                "max_rules": 10,
                "max_dashboards": 2,
                "max_api_calls_per_day": 10_000,
                "max_messages_per_month": 10_000,
                "data_retention_days": 7,
                "features": ["basic_dashboards"],
            },
        },
        {
            "code": "starter",
            "name": "Starter",
            "description": "Small deployments",
            "monthly_price_idr": 100_000,
            "yearly_price_idr": 1_000_000,
            "display_order": 2,
            "limits": {
                "max_devices": 20,
                "max_users": 3,
                "max_rules": 50,
                "max_dashboards": 5,
                "max_api_calls_per_day": 50_000,
                "max_messages_per_month": 100_000,
                "data_retention_days": 30,
                "features": ["basic_dashboards", "advanced_charts"],
            },
        },
        {
            "code": "pro",
            "name": "Pro",
            "description": "Production IoT fleets",
            "monthly_price_idr": 500_000,
            "yearly_price_idr": 5_000_000,
            "display_order": 3,
            "limits": {
                "max_devices": 100,
                "max_users": 10,
                "max_rules": 200,
                "max_dashboards": 20,
                "max_api_calls_per_day": 200_000,
                "max_messages_per_month": 1_000_000,
                "data_retention_days": 90,
                "features": ["basic_dashboards", "advanced_charts", "custom_branding", "audit_log_export"],
            },
        },
        {
            "code": "enterprise",
            "name": "Enterprise",
            "description": "Large scale + compliance",
            "monthly_price_idr": 5_000_000,
            "yearly_price_idr": 50_000_000,
            "display_order": 4,
            "limits": {
                "max_devices": None,
                "max_users": 50,
                "max_rules": None,
                "max_dashboards": None,
                "max_api_calls_per_day": None,
                "max_messages_per_month": 10_000_000,
                "data_retention_days": 730,
                "features": [
                    "basic_dashboards",
                    "advanced_charts",
                    "custom_branding",
                    "white_label",
                    "sso",
                    "audit_log_export",
                    "priority_support",
                    "sla_99_9",
                    "dedicated_server",
                ],
            },
        },
    ]
