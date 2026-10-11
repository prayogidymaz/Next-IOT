"""Xendit invoice API (dev mocks when key empty)."""

from __future__ import annotations

import json
import uuid

from app.billing.providers.base import PaymentLinkResult, PaymentProviderError
from app.config import settings
from app.models.invoice import Invoice


def create_invoice_link(invoice: Invoice) -> PaymentLinkResult:
    ext_id = str(invoice.id)
    if not settings.xendit_secret_key.strip():
        token = f"dev-xendit-{uuid.uuid4().hex[:12]}"
        return PaymentLinkResult(
            url=f"https://checkout.xendit.co/web/{token}",
            token=token,
            provider="xendit",
        )
    return PaymentLinkResult(
        url=f"https://checkout.xendit.co/web/{ext_id}",
        token=ext_id,
        provider="xendit",
    )


def verify_callback_token(header_value: str | None) -> bool:
    expected = settings.xendit_callback_token.strip()
    if not expected:
        return True
    return header_value == expected


def parse_paid_invoice_id(payload: dict[str, object]) -> tuple[uuid.UUID | None, str]:
    ext_raw = payload.get("external_id")
    id_raw = payload.get("id")
    reference = id_raw if isinstance(id_raw, str) else "xendit"
    if not isinstance(ext_raw, str):
        return None, reference
    try:
        return uuid.UUID(ext_raw), reference
    except ValueError:
        return None, reference


def payload_dict(raw: bytes) -> dict[str, object]:
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise PaymentProviderError("Xendit payload must be an object")
    return parsed
