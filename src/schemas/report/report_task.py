from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict
import uuid

from pydantic import BaseModel, Field


class Status(str, Enum):
    pending = "pending"
    ready = "ready"
    error = "error"


class ReportTaskAdd(BaseModel):
    user_id: uuid.UUID
    template_id: int
    status: Status = Status.pending
    parameters: str | None = None  # например: JSON-строка с фильтрами
    result_file: str | None = Field(
        default=None, max_length=255
    )  # путь или ссылка на файл
    error_message: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReportRequest(BaseModel):
    report_name: str = Field(..., description="Название отчета")
    parameters: Dict[str, Any] = Field(
        ..., description="Параметры отчета в формате JSON"
    )


class ReportTaskReady(BaseModel):
    status: Status = Status.pending
    result_file: str | None = Field(default=None, max_length=255)


class ReportTaskStatus(BaseModel):
    task_id: uuid.UUID
    status: Status = Status.pending
    result_file: str | None = Field(default=None, max_length=255)
    error_message: str | None = None


class ReportTask(ReportTaskAdd):
    id: uuid.UUID
