from datetime import datetime
from pydantic import BaseModel, Field


class RefreshTokenAdd(BaseModel):
    user_id: int
    token: str = Field(min_length=1, max_length=255)
    device: str | None = Field(default=None, max_length=100)
    ip_address: str | None = Field(default=None, max_length=45)
    expires_at: datetime


class RefreshToken(RefreshTokenAdd):
    id: int