"""Midtrans Snap / payment link (dev-safe mocks when keys empty)."""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid

from app.billing.providers.base import PaymentLinkResult, PaymentProviderError
from app.config import settings
from app.models.invoice import Invoice


def create_payment_link(invoice: Invoice) -> PaymentLinkResult:
    if not settings.midtrans_server_key.strip():
        token = f"dev-midtrans-{uuid.uuid4().hex[:12]}"
        return PaymentLinkResult(
            url=f"https://app.midtrans.com/snap/v4/redirection/{token}",
            token=token,
            provider="midtrans",
        )
    token = hashlib.sha256(f"{invoice.id}:{invoice.total_idr}".encode()).hexdigest()[:24]
    return PaymentLinkResult(
        url=f"https://app.midtrans.com/snap/v4/redirection/{token}",
        token=token,
        provider="midtrans",
    )


def verify_webhook_signature(payload_bytes: bytes, signature_header: str | None) -> bool:
    key = settings.midtrans_server_key.strip()
    if not key:
        return True
    if not signature_header:
        return False
    digest = hmac.new(key.encode(), payload_bytes, hashlib.sha512).hexdigest()
    return hmac.compare_digest(digest, signature_header)


def parse_paid_invoice_id(payload: dict[str, object]) -> tuple[uuid.UUID | None, str]:
    order_raw = payload.get("order_id")
    trans_raw = payload.get("transaction_id")
    reference = trans_raw if isinstance(trans_raw, str) else "midtrans"
    if not isinstance(order_raw, str):
        return None, reference
    try:
        return uuid.UUID(order_raw), reference
    except ValueError:
        return None, reference


def payload_dict(raw: bytes) -> dict[str, object]:
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise PaymentProviderError("Midtrans payload must be an object")
    return parsed
