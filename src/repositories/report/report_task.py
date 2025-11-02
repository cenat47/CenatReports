from src.models.report.report_task import ReportTaskORM
from src.repositories.base import BaseRepository
from src.repositories.mapper.mappers import ReportTaskDataMapper


class ReportTaskRepository(BaseRepository):
    model = ReportTaskORM
    mapper = ReportTaskDataMapper
