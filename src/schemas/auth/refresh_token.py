import uuid
from datetime import datetime

from pydantic import BaseModel


class RefreshTokenAdd(BaseModel):
    user_id: uuid.UUID
    refresh_token: uuid.UUID
    expires_at: datetime
    ip_address: str | None = None


class RefreshToken(RefreshTokenAdd):
    id: uuid.UUID
    created_at: datetime


class Token(BaseModel):
    access_token: str
    refresh_token: uuid.UUID
    token_type: str
