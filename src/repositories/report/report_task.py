from src.repositories.mapper.mappers import ReportTaskDataMapper
from src.models.report.report_task import ReportTaskORM
from src.repositories.base import BaseRepository


class ReportTaskRepository(BaseRepository):
    model = ReportTaskORM
    mapper = ReportTaskDataMapper