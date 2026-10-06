import uuid
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.deps import DbSession
from app.devices.security import verify_device_secret
from app.models.device_credential import DeviceCredential

device_basic = HTTPBasic(auto_error=False)


@dataclass(frozen=True)
class CurrentDevice:
    device_id: uuid.UUID
    tenant_id: uuid.UUID
    client_id: str
    status: str


async def get_current_device(
    credentials: Annotated[HTTPBasicCredentials | None, Depends(device_basic)],
    db: DbSession,
) -> CurrentDevice:
    """Device auth via HTTP Basic: username=client_id, password=client_secret."""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Device authentication required")

    result = await db.scalar(
        select(DeviceCredential)
        .options(selectinload(DeviceCredential.device))
        .where(DeviceCredential.client_id == credentials.username)
    )
    if not result or not result.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid device credentials")

    if result.secret_hash is None:
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


RequireDevice = Annotated[CurrentDevice, Depends(get_current_device)]
