"""OTA firmware catalog for edge devices."""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.devices.edge_agent.models import FirmwareVersionRow
from app.devices.edge_agent.schemas import FirmwareVersionView


class OTAService:
    def __init__(self, storage_dir: str | None = None) -> None:
        self._storage_dir = Path(storage_dir or settings.firmware_upload_dir)

    async def get_latest_firmware(self, db: AsyncSession, device_type: str) -> FirmwareVersionView | None:
        row = await db.scalar(
            select(FirmwareVersionRow)
            .where(FirmwareVersionRow.device_type == device_type, FirmwareVersionRow.stable.is_(True))
            .order_by(FirmwareVersionRow.released_at.desc())
            .limit(1)
        )
        if row is None:
            return None
        return _to_view(row)

    async def upload_firmware(
        self,
        db: AsyncSession,
        device_type: str,
        version: str,
        binary: bytes,
    ) -> FirmwareVersionView:
        checksum = hashlib.sha256(binary).hexdigest()
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{device_type}-{version}.bin"
        path = self._storage_dir / filename
        path.write_bytes(binary)
        url = f"/firmware/{filename}"
        row = FirmwareVersionRow(
            device_type=device_type,
            version=version,
            binary_url=url,
            checksum=checksum,
            released_at=datetime.now(tz=UTC),
            stable=True,
        )
        db.add(row)
        await db.flush()
        return _to_view(row)

    async def list_versions(self, db: AsyncSession, device_type: str) -> list[FirmwareVersionView]:
        rows = list(
            (
                await db.scalars(
                    select(FirmwareVersionRow)
                    .where(FirmwareVersionRow.device_type == device_type)
                    .order_by(FirmwareVersionRow.released_at.desc())
                )
            ).all()
        )
        return [_to_view(row) for row in rows]

    def validate_checksum(self, binary: bytes, expected: str) -> bool:
        digest = hashlib.sha256(binary).hexdigest()
        return digest.lower() == expected.lower()

    async def validate_checksum_url(self, db: AsyncSession, firmware_id: uuid.UUID, expected: str) -> bool:
        row = await db.get(FirmwareVersionRow, firmware_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Firmware not found")
        path = self._storage_dir / Path(row.binary_url).name
        if not path.is_file():
            return row.checksum.lower() == expected.lower()
        return self.validate_checksum(path.read_bytes(), expected)


def _to_view(row: FirmwareVersionRow) -> FirmwareVersionView:
    return FirmwareVersionView(
        id=row.id,
        device_type=row.device_type,
        version=row.version,
        url=row.binary_url,
        checksum=row.checksum,
        released_at=row.released_at,
        stable=row.stable,
    )
