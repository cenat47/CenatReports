from datetime import datetime
from pydantic import BaseModel, Field


class ReportTaskAdd(BaseModel):
    user_id: int
    template_id: int
    status: str = Field(default="pending")  # pending, ready, error
    parameters: str | None = None  # например: JSON-строка с фильтрами
    result_file: str | None = Field(default=None, max_length=255)  # путь или ссылка на файл
    error_message: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReportTask(ReportTaskAdd):
    id: int
