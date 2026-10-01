import hashlib
import uuid
from pathlib import Path

from fastapi import HTTPException, status

from app.config import settings

ALLOWED_FIRMWARE_SUFFIXES = {".bin", ".elf"}


def _upload_root() -> Path:
    root = Path(settings.firmware_upload_dir)
    root.mkdir(parents=True, exist_ok=True)
    return root


def save_firmware_blob(tenant_id: uuid.UUID, release_id: uuid.UUID, filename: str, data: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_FIRMWARE_SUFFIXES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Firmware file must be one of: {', '.join(sorted(ALLOWED_FIRMWARE_SUFFIXES))}",
        )
    if len(data) > settings.firmware_max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Firmware exceeds {settings.firmware_max_upload_bytes} bytes",
        )

    tenant_dir = _upload_root() / str(tenant_id)
    tenant_dir.mkdir(parents=True, exist_ok=True)
    path = tenant_dir / f"{release_id}{suffix}"
    path.write_bytes(data)
    return f"/api/v1/ota/device/releases/{release_id}/download"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resolve_firmware_path(tenant_id: uuid.UUID, release_id: uuid.UUID) -> Path | None:
    tenant_dir = _upload_root() / str(tenant_id)
    for suffix in ALLOWED_FIRMWARE_SUFFIXES:
        candidate = tenant_dir / f"{release_id}{suffix}"
        if candidate.is_file():
            return candidate
    return None
