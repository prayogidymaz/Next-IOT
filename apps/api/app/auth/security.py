import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from pydantic import JsonValue

from app.config import settings

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def _build_expiry(minutes: int = 0, days: int = 0) -> datetime:
    return datetime.now(UTC) + timedelta(minutes=minutes, days=days)


def _encode_jwt(payload: dict[str, JsonValue]) -> str:
    encoded = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    if isinstance(encoded, str):
        return encoded
    return encoded.decode("utf-8")


def create_access_token(*, user_id: uuid.UUID, tenant_id: uuid.UUID, role: str) -> str:
    payload: dict[str, JsonValue] = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "role": role,
        "type": TOKEN_TYPE_ACCESS,
        "iat": int(datetime.now(UTC).timestamp()),
        "exp": int(_build_expiry(minutes=settings.jwt_access_token_expire_minutes).timestamp()),
    }
    return _encode_jwt(payload)


def create_refresh_token(*, user_id: uuid.UUID, tenant_id: uuid.UUID) -> tuple[str, str]:
    jti = str(uuid.uuid4())
    payload: dict[str, JsonValue] = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "jti": jti,
        "type": TOKEN_TYPE_REFRESH,
        "iat": int(datetime.now(UTC).timestamp()),
        "exp": int(_build_expiry(days=settings.jwt_refresh_token_expire_days).timestamp()),
    }
    return _encode_jwt(payload), jti


def decode_token(token: str) -> dict[str, JsonValue]:
    from pydantic import TypeAdapter

    claims_adapter = TypeAdapter(dict[str, JsonValue])
    raw = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    return claims_adapter.validate_python(raw)
