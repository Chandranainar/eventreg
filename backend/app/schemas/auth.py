from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)

    @field_validator("email", mode="before")
    @classmethod
    def normalise_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class AdminUserRead(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    last_login_at: datetime | None
    csrf_token: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    success: bool = True
    user: AdminUserRead
