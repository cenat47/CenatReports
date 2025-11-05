from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class Status(str, Enum):
    pending = "pending"
    ready = "ready"
    error = "error"


class ReportTaskAdd(BaseModel):
    user_id: int
    template_id: int
    status: Status = Status.pending
    parameters: str | None = None  # например: JSON-строка с фильтрами
    result_file: str | None = Field(
        default=None, max_length=255
    )  # путь или ссылка на файл
    error_message: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReportTask(ReportTaskAdd):
    id: int
