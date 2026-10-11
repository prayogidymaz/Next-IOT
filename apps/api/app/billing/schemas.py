"""Billing API schemas."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PlanLimitsSchema(BaseModel):
    max_devices: int | None = None
    max_users: int | None = None
    max_rules: int | None = None
    max_dashboards: int | None = None
    max_api_calls_per_day: int | None = None
    max_messages_per_month: int | None = None
    data_retention_days: int = 7
    features: list[str] = Field(default_factory=list)


class SubscriptionPlanResponse(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    description: str | None
    monthly_price_idr: int | None
    yearly_price_idr: int | None
    limits: PlanLimitsSchema
    display_order: int

    model_config = ConfigDict(from_attributes=True)


class TenantSubscriptionResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    plan_code: str
    plan_name: str
    status: str
    billing_cycle: str
    trial_ends_at: datetime | None
    current_period_start: datetime | None
    current_period_end: datetime | None
    cancel_at_period_end: bool


class UsageSummaryResponse(BaseModel):
    devices_used: int
    devices_limit: int | None
    messages_used: int
    messages_limit: int | None
    api_calls_used: int
    api_calls_limit: int | None


class InvoiceResponse(BaseModel):
    id: uuid.UUID
    invoice_number: str
    period_start: date
    period_end: date
    subtotal_idr: int
    tax_idr: int
    total_idr: int
    status: str
    due_date: date
    paid_at: datetime | None
    pdf_url: str | None

    model_config = ConfigDict(from_attributes=True)


class ChangePlanRequest(BaseModel):
    plan_code: str = Field(min_length=2, max_length=32)
    billing_cycle: str = Field(default="monthly", pattern="^(monthly|yearly)$")


class PaymentMethodCreateRequest(BaseModel):
    provider: str = Field(pattern="^(midtrans|xendit)$")
    type: str = Field(pattern="^(credit_card|bank_transfer|ewallet)$")
    details: dict[str, str] = Field(default_factory=dict)
    is_default: bool = False
