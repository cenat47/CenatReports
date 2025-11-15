from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class ReportTemplateORM(Base):
    __tablename__ = "report_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    allowed_roles: Mapped[str | None] = mapped_column(String(200))
