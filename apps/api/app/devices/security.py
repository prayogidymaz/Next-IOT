import hashlib
import secrets
import uuid

from app.auth.security import hash_password, verify_password


def generate_provisioning_token() -> str:
    return f"prov_{secrets.token_urlsafe(32)}"


def hash_provisioning_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_client_id() -> str:
    return f"dev_{uuid.uuid4().hex}"


def generate_client_secret() -> str:
    return secrets.token_urlsafe(48)


def hash_device_secret(secret: str) -> str:
    return hash_password(secret)


def verify_device_secret(secret: str, secret_hash: str) -> bool:
    return verify_password(secret, secret_hash)
