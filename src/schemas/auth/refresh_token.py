from datetime import datetime
import uuid
from pydantic import BaseModel, Field


class RefreshTokenAdd(BaseModel):
    user_id: uuid.UUID
    refresh_token: uuid.UUID
    expires_at: datetime
    ip_address: str | None = None


class RefreshToken(RefreshTokenAdd):
    id: uuid.UUID
    created_at: datetime
