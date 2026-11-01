"""Marketplace template ORM."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class WorkflowTemplate(Base):
    __tablename__ = "workflow_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    tags_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    author_tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    snapshot_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    downloads_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rating_avg: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    rating_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    locale: Mapped[str] = mapped_column(String(8), nullable=False, default="id")
    price_idr: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stripe_product_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    author_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


class MarketplaceSeller(Base):
    __tablename__ = "marketplace_sellers"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    tier: Mapped[str] = mapped_column(String(16), nullable=False, default="bronze")
    commission_rate_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("15"))
    lifetime_sales_idr: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    verified_badge: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MarketplacePayout(Base):
    __tablename__ = "marketplace_payouts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("marketplace_sellers.user_id", ondelete="CASCADE"), nullable=False
    )
    period_month: Mapped[str] = mapped_column(String(7), nullable=False)
    gross_sales_idr: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    commission_idr: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    transaction_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)


class MarketplaceTemplatePurchase(Base):
    __tablename__ = "marketplace_template_purchases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflow_templates.id", ondelete="CASCADE"), nullable=False
    )
    buyer_tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    amount_idr: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_provider: Mapped[str] = mapped_column(String(32), nullable=False, default="midtrans")
    payment_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="paid")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class WorkflowTemplateRating(Base):
    __tablename__ = "workflow_template_ratings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflow_templates.id", ondelete="CASCADE"), nullable=False
    )
    rater_tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    review_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class WorkflowTemplateDownload(Base):
    __tablename__ = "workflow_template_downloads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflow_templates.id", ondelete="CASCADE"), nullable=False
    )
    downloader_tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    downloaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
