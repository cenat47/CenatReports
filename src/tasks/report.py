# services/report.py
from datetime import date
import json
import csv
import os

from pydantic_core import ValidationError
from src.schemas.report.report_task import ReportTaskReady, Status
from src.schemas.report.sales_daily import SalesDailyParams
from src.utils.db_manager import DBManager
from src.database import async_session_maker_null_pооl


class BaseService:
    def __init__(self, db: DBManager | None = None):
        self.db = db


async def get_db_np():
    async with DBManager(session_factory=async_session_maker_null_pооl) as db:
        yield db


class ReportService(BaseService):
    async def make_sales_daily_report(self, task_id: str, params: dict):
        try:
            validated_params = SalesDailyParams(**params)
        except ValidationError as e:
            print(f"Ошибка валидации параметров: {e}")
            return
        sales_data = await self.db.sales_daily.get_sales_daily(
            date_to=validated_params.date_to, date_from=validated_params.date_from
        )
        # TODO Проверяем, есть ли данные
        os.makedirs("report", exist_ok=True)
        file_path = f"report/{task_id}.csv"
        sales_data_dicts = [row.model_dump() for row in sales_data]
        headers = sales_data_dicts[0].keys()

        with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(sales_data_dicts)

        await self.db.report_task.edit(
            ReportTaskReady(status=Status.ready, result_file=file_path), id=task_id
        )
        await self.db.commit()

    async def make_report_h(self, task_id):
        task = await self.db.report_task.get_one_or_none(id=task_id)
        if task is None:
            raise ValueError(f"Task with id {task_id} not found")

        report_template = await self.db.report_template.get_one_or_none(
            id=task.template_id
        )
        if report_template is None:
            raise ValueError(f"Report template with id {task.template_id} not found")

        report_name = report_template.name
        params = json.loads(task.parameters)

        if report_name == "daily_sales":
            await self.make_sales_daily_report(task_id=task_id, params=params)
