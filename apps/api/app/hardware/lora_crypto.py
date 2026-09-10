"""LoRa AES helpers — prefers packages/shared with Docker-safe fallback."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from app.hardware import lora_crypto_core as _fallback


def _load_shared_module():
    candidates: list[Path] = [Path("/packages/shared/lora_crypto.py")]
    resolved = Path(__file__).resolve().parents
    if len(resolved) > 4:
        candidates.append(resolved[4] / "packages" / "shared" / "lora_crypto.py")
    for shared_path in candidates:
        if not shared_path.exists():
            continue
        spec = importlib.util.spec_from_file_location("next_iot_shared_lora_crypto", shared_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            return module
    return None


_shared = _load_shared_module() or _fallback

AES128_KEY_BYTES = _shared.AES128_KEY_BYTES
LoRaCipherMode = _shared.LoRaCipherMode
parse_aes128_key = _shared.parse_aes128_key
encrypt_aes128_cbc = _shared.encrypt_aes128_cbc
decrypt_aes128_cbc = _shared.decrypt_aes128_cbc
encrypt_aes128_gcm = _shared.encrypt_aes128_gcm
decrypt_aes128_gcm = _shared.decrypt_aes128_gcm
format_encrypted_line = _shared.format_encrypted_line
is_encrypted_line = _shared.is_encrypted_line
encrypt_serial_payload = _shared.encrypt_serial_payload
decrypt_serial_line = _shared.decrypt_serial_line
maybe_decrypt_serial_line = _shared.maybe_decrypt_serial_line
