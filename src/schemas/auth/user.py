from datetime import datetime
import uuid
from pydantic import BaseModel, Field, EmailStr


class UserRequest(BaseModel):
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=1, max_length=75)
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)

class UserAdd(BaseModel):
    email: EmailStr
    password_hash: str
    first_name: str | None
    last_name: str | None
    role: str = "user"
    is_active: bool = True
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: datetime | None = None


class User(UserAdd):
    id: uuid.UUID
