from sqlalchemy import String, Text, ForeignKey, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from typing import Optional, Any
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base
import uuid


class AuditORM(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Кто совершил действие
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Тип действия: LOGIN, LOGOUT, CREATE, UPDATE, DELETE, DOWNLOAD, FAILED_LOGIN
    action: Mapped[str] = mapped_column(String(50), index=True)

    # Название затронутой таблицы (опционально для действий типа LOGIN)
    table_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # ID записи, над которой совершено действие
    record_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Старые и новые значения в формате JSON
    old_values: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Информация о клиенте
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Дополнительные детали (например, причина ошибки)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Время события
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now(), index=True
    )
