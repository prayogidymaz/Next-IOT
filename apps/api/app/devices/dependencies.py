import uuid
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.deps import get_db
from app.devices.security import verify_device_secret
from app.models.device import Device
from app.models.device_credential import DeviceCredential

device_basic = HTTPBasic(auto_error=False)


@dataclass(frozen=True)
class CurrentDevice:
    device_id: uuid.UUID
    tenant_id: uuid.UUID
    client_id: str
    status: str


async def get_current_device(
    credentials: HTTPBasicCredentials | None = Depends(device_basic),
    db: AsyncSession = Depends(get_db),
) -> CurrentDevice:
    """Device auth via HTTP Basic: username=client_id, password=client_secret."""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Device authentication required")

    result = await db.scalar(
        select(DeviceCredential)
        .options(selectinload(DeviceCredential.device))
        .where(DeviceCredential.client_id == credentials.username)
    )
    if not result or result.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid device credentials")

    if not verify_device_secret(credentials.password, result.secret_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid device credentials")

    device = result.device
    if device.status == "deactivated":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Device is deactivated")

    return CurrentDevice(
        device_id=device.id,
        tenant_id=device.tenant_id,
        client_id=result.client_id,
        status=device.status,
    )


RequireDevice = Depends(get_current_device)
