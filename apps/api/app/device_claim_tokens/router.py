import uuid

from app.auth.dependencies import RequireOperator, RequireTenantAdmin
from app.deps import DbSession, RedisDep
from app.device_claim_tokens import service
from app.device_claim_tokens.schemas import (
    DeviceClaimResultResponse,
    DeviceClaimTokenCreateRequest,
    DeviceClaimTokenResponse,
)
from fastapi import APIRouter, status

router = APIRouter(prefix="/api/v1/device-claim-tokens", tags=["device-claim-tokens"])


@router.get("", response_model=list[DeviceClaimTokenResponse])
async def list_device_claim_tokens(user: RequireOperator, db: DbSession) -> list[DeviceClaimTokenResponse]:
    return await service.list_claim_tokens(db, user)


@router.post("", response_model=DeviceClaimTokenResponse, status_code=status.HTTP_201_CREATED)
async def create_device_claim_token(
    payload: DeviceClaimTokenCreateRequest,
    user: RequireTenantAdmin,
    db: DbSession,
) -> DeviceClaimTokenResponse:
    return await service.create_claim_token(db, user, payload)


@router.post("/{claim_token}/claim", response_model=DeviceClaimResultResponse)
async def claim_device_with_token(
    claim_token: str,
    db: DbSession,
    redis: RedisDep,
) -> DeviceClaimResultResponse:
    return await service.claim_device(db, redis, claim_token)


@router.delete("/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_device_claim_token(
    token_id: uuid.UUID,
    user: RequireTenantAdmin,
    db: DbSession,
) -> None:
    await service.revoke_claim_token(db, user, token_id)
