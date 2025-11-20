from pydantic import BaseModel, Field


class ReportTemplateAdd(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    allowed_roles: str | None = Field(default=None, max_length=200)


class ReportTemplate(ReportTemplateAdd):
    id: int
