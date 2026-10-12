"""Crypto and worker tests."""

from __future__ import annotations

import pytest
from app.agriculture.crypto import decrypt_app_key, encrypt_app_key
from app.agriculture.worker import run_disease_scan_once


def test_lora_key_roundtrip() -> None:
    plain = "00112233445566778899AABBCCDDEEFF"
    enc = encrypt_app_key(plain)
    assert decrypt_app_key(enc) == plain


@pytest.mark.asyncio
async def test_disease_scan_runs(test_redis) -> None:
    count = await run_disease_scan_once(test_redis)
    assert count >= 0
