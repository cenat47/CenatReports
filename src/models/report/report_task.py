from datetime import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy import ForeignKey, String, Text, func, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class ReportTaskORM(Base):
    __tablename__ = "report_tasks"
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id"))
    template_id: Mapped[int] = mapped_column(ForeignKey("report_templates.id"))

    status: Mapped[str] = mapped_column(
        String(50), default="pending"
    )  # pending, ready, error
    parameters: Mapped[str | None] = mapped_column(
        Text
    )  # например: JSON-строка с фильтрами
    result_file: Mapped[str | None] = mapped_column(
        String(255)
    )  # путь или ссылка на файл
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=func.now()
    )
