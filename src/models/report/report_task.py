from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class ReportTask(Base):
    __tablename__ = "report_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
