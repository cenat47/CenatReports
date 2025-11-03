from datetime import datetime
import uuid
import sqlalchemy as sa
from sqlalchemy import UUID, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class RefreshTokenORM(Base):
    __tablename__ = 'refresh_token'

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    refresh_token: Mapped[uuid.UUID] = mapped_column(UUID, index=True, unique=True)
    expires_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True),
                                                 server_default=func.now())
    ip_address: Mapped[str] = mapped_column(sa.String(45), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, sa.ForeignKey(
        "users.id", ondelete="CASCADE"))