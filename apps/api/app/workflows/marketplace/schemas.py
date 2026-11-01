"""Marketplace API schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.types.json_types import JsonObject


class WorkflowTemplateView(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    category: str
    tags_json: list[str]
    author_tenant_id: uuid.UUID
    author_tenant_name: str = ""
    snapshot_json: JsonObject
    downloads_count: int
    rating_avg: float
    rating_count: int
    published: bool
    created_at: datetime
    locale: str
    price_idr: int = 0
    author_user_id: uuid.UUID | None = None


class PublishTemplateBody(BaseModel):
    workflow_id: uuid.UUID
    name: str
    description: str = ""
    category: str
    tags: list[str] = Field(default_factory=list)
    locale: str = "id"


class RateTemplateBody(BaseModel):
    rating: int = Field(ge=1, le=5)
    review: str = ""


class DownloadTemplateBody(BaseModel):
    target_tenant_id: uuid.UUID | None = None


class CheckoutResponse(BaseModel):
    provider: str
    amount_idr: int
    checkout_url: str
    payment_ref: str | None = None


class SellerDashboardView(BaseModel):
    tier: str
    lifetime_sales_idr: int
    commission_rate_percent: float
    verified_badge: bool
    pending_payout_idr: int


class PayoutView(BaseModel):
    id: uuid.UUID
    period_month: str
    gross_sales_idr: int
    commission_idr: int
    status: str
    paid_at: datetime | None
    transaction_ref: str | None

    model_config = {"from_attributes": True}
