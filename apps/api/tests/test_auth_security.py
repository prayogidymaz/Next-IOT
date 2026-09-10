import uuid

import jwt
import pytest

from app.auth.security import (
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.config import settings


def test_password_hash_and_verify():
    hashed = hash_password("SecurePass123!")
    assert hashed != "SecurePass123!"
    assert verify_password("SecurePass123!", hashed)
    assert not verify_password("WrongPassword!", hashed)


def test_access_token_contains_tenant_claim():
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    token = create_access_token(user_id=user_id, tenant_id=tenant_id, role="tenant_admin")
    payload = decode_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["tenant_id"] == str(tenant_id)
    assert payload["role"] == "tenant_admin"
    assert payload["type"] == TOKEN_TYPE_ACCESS


def test_refresh_token_has_jti():
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    token, jti = create_refresh_token(user_id=user_id, tenant_id=tenant_id)
    payload = decode_token(token)

    assert payload["jti"] == jti
    assert payload["type"] == TOKEN_TYPE_REFRESH
    assert payload["tenant_id"] == str(tenant_id)


def test_invalid_token_raises():
    with pytest.raises(jwt.PyJWTError):
        decode_token("not.a.valid.token")
