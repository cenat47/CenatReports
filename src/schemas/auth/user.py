import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    user = "user"
    manager = "manager"
    admin = "admin"
    superadmin = "superadmin"


class UserRequest(BaseModel):
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=1, max_length=75)
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)


class UserVerify(BaseModel):
    email: EmailStr = Field(max_length=100)
    code: str = Field(pattern=r"^\d{6}$")


class UserReverify(BaseModel):
    email: EmailStr


class VerifyStatus(BaseModel):
    is_verified: bool = False


class UserLogin(BaseModel):
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=1, max_length=75)


class UserAdd(BaseModel):
    email: EmailStr
    password_hash: str
    first_name: str | None
    last_name: str | None
    role: UserRole = UserRole.user
    is_active: bool = True
    is_verified: bool = False
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: datetime | None = None


class LastLoginUpdate(BaseModel):
    last_login_at: datetime


class User(UserAdd):
    id: uuid.UUID


class UserRoleUpdate(BaseModel):
    email: EmailStr
    new_role: UserRole


class UserRoleUpdateConfirm(BaseModel):
    email: EmailStr
    new_role: UserRole
    code: str = Field(pattern=r"^\d{6}$")


class UserRoleEdit(BaseModel):
    role: UserRole
