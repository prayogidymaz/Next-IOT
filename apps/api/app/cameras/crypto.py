"""Encrypt camera RTSP credentials at rest."""

from __future__ import annotations

from app.agriculture.crypto import decrypt_app_key, encrypt_app_key


def encrypt_camera_username(plain: str) -> str:
    return encrypt_app_key(plain)


def decrypt_camera_username(token: str) -> str:
    return decrypt_app_key(token)
