from datetime import datetime
import uuid
from sqlalchemy import UUID, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    role: Mapped[str] = mapped_column(
        String(50), default="user"
    )  # допустимы: admin, manager, user

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)
