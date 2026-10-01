import re
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    tenant_name: str | None = Field(default=None, min_length=2, max_length=255)
    tenant_slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )

    @model_validator(mode="after")
    def apply_default_tenant(self) -> "RegisterRequest":
        local = self.email.split("@")[0].lower()
        slug_base = re.sub(r"[^a-z0-9]+", "-", local).strip("-") or "workspace"
        if not self.tenant_slug:
            self.tenant_slug = slug_base[:80]
        if not self.tenant_name:
            self.tenant_name = f"{local.replace('-', ' ').title()} Workspace"
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str | None = None
    user_id: uuid.UUID | None = None
    email: EmailStr | None = None


class AuthMeResponse(BaseModel):
    user_id: uuid.UUID
    email: EmailStr
    role: str
    tenant_id: uuid.UUID
    permissions: list[str]


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    role: str
    tenant_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class RegisterResponse(BaseModel):
    tenant_id: uuid.UUID
    tenant_slug: str
    user: UserResponse
    tokens: TokenResponse


class MessageResponse(BaseModel):
    message: str
