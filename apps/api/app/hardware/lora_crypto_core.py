"""Bundled AES-128 LoRa crypto (Docker fallback mirror of packages/shared/lora_crypto.py)."""

from __future__ import annotations

import binascii
import os
import re
from enum import StrEnum

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

AES128_KEY_BYTES = 16
CBC_IV_BYTES = 16
GCM_NONCE_BYTES = 12
GCM_TAG_BYTES = 16

ENC_PREFIX_CBC = "ENC:"
ENC_PREFIX_GCM = "AESGCM:"


class LoRaCipherMode(StrEnum):
    CBC = "AES-128-CBC"
    GCM = "AES-128-GCM"


def parse_aes128_key(raw: str | None) -> bytes | None:
    if raw is None:
        return None
    value = raw.strip()
    if not value:
        return None
    if re.fullmatch(r"[0-9a-fA-F]{32}", value):
        return bytes.fromhex(value)
    try:
        decoded = binascii.a2b_base64(value)
    except binascii.Error:
        return None
    if len(decoded) != AES128_KEY_BYTES:
        raise ValueError("LORA_ENCRYPTION_KEY must decode to 16 bytes for AES-128")
    return decoded


def encrypt_aes128_cbc(plaintext: bytes, key: bytes) -> bytes:
    if len(key) != AES128_KEY_BYTES:
        raise ValueError("AES-128-CBC requires a 16-byte key")
    iv = os.urandom(CBC_IV_BYTES)
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return iv + ciphertext


def decrypt_aes128_cbc(payload: bytes, key: bytes) -> bytes:
    if len(key) != AES128_KEY_BYTES:
        raise ValueError("AES-128-CBC requires a 16-byte key")
    if len(payload) < CBC_IV_BYTES + 1:
        raise ValueError("CBC payload too short")
    iv, ciphertext = payload[:CBC_IV_BYTES], payload[CBC_IV_BYTES:]
    decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(padded) + unpadder.finalize()


def encrypt_aes128_gcm(plaintext: bytes, key: bytes, *, associated_data: bytes | None = None) -> bytes:
    if len(key) != AES128_KEY_BYTES:
        raise ValueError("AES-128-GCM requires a 16-byte key")
    nonce = os.urandom(GCM_NONCE_BYTES)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
    return nonce + ciphertext


def decrypt_aes128_gcm(payload: bytes, key: bytes, *, associated_data: bytes | None = None) -> bytes:
    if len(key) != AES128_KEY_BYTES:
        raise ValueError("AES-128-GCM requires a 16-byte key")
    if len(payload) < GCM_NONCE_BYTES + GCM_TAG_BYTES + 1:
        raise ValueError("GCM payload too short")
    nonce, ciphertext = payload[:GCM_NONCE_BYTES], payload[GCM_NONCE_BYTES:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, associated_data)


def format_encrypted_line(payload: bytes, mode: LoRaCipherMode = LoRaCipherMode.CBC) -> str:
    prefix = ENC_PREFIX_CBC if mode == LoRaCipherMode.CBC else ENC_PREFIX_GCM
    return f"{prefix}{payload.hex()}"


def is_encrypted_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith(ENC_PREFIX_CBC) or stripped.startswith(ENC_PREFIX_GCM)


def encrypt_serial_payload(
    plaintext: str,
    key: bytes,
    *,
    mode: LoRaCipherMode = LoRaCipherMode.CBC,
) -> str:
    data = plaintext.encode("utf-8")
    if mode == LoRaCipherMode.GCM:
        blob = encrypt_aes128_gcm(data, key)
    else:
        blob = encrypt_aes128_cbc(data, key)
    return format_encrypted_line(blob, mode=mode)


def decrypt_serial_line(line: str, key: bytes) -> str:
    stripped = line.strip()
    if stripped.startswith(ENC_PREFIX_CBC):
        blob = bytes.fromhex(stripped[len(ENC_PREFIX_CBC) :])
        plain = decrypt_aes128_cbc(blob, key)
    elif stripped.startswith(ENC_PREFIX_GCM):
        blob = bytes.fromhex(stripped[len(ENC_PREFIX_GCM) :])
        plain = decrypt_aes128_gcm(blob, key)
    elif re.fullmatch(r"[0-9a-fA-F]+", stripped):
        blob = bytes.fromhex(stripped)
        plain = decrypt_aes128_cbc(blob, key)
    else:
        raise ValueError("Unsupported encrypted LoRa payload format")
    return plain.decode("utf-8")


def maybe_decrypt_serial_line(line: str, key: bytes | None) -> str:
    if not is_encrypted_line(line):
        return line
    if key is None:
        raise ValueError("Encrypted LoRa payload received but LORA_ENCRYPTION_KEY is not configured")
    return decrypt_serial_line(line, key)
