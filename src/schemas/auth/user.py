from datetime import datetime
from pydantic import BaseModel, Field


class UserAdd(BaseModel):
    email: str = Field(min_length=1, max_length=100)
    password_hash: str = Field(min_length=1, max_length=255)

    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    role: str = Field(default="user", max_length=50)  # допустимы: admin, manager, user

    is_active: bool = True
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: datetime | None = None


class User(UserAdd):
    id: int
