"""Payment provider protocol."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PaymentLinkResult:
    url: str
    token: str
    provider: str


class PaymentProviderError(Exception):
    pass
