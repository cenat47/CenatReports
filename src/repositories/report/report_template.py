from src.repositories.mapper.mappers import ReportTemplateDataMapper
from src.models.report.report_template import ReportTemplateORM
from src.repositories.base import BaseRepository


class ReportTemplateRepository(BaseRepository):
    model = ReportTemplateORM
    mapper = ReportTemplateDataMapper