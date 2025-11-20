# services/report.py
import json
import csv
import os

from pydantic_core import ValidationError
from src.schemas.report.payments_by_method import PaymentsReportParams
from src.schemas.report.sales_by_customer import SalesByCustomerParams
from src.schemas.report.sales_by_product_category_daily import (
    SalesByCategoryDailyParams,
    SalesByProductDailyParams,
)
from src.schemas.report.report_task import ReportTaskReady, Status
from src.schemas.report.sales_daily import SalesDailyParams
from src.utils.db_manager import DBManager
from src.database import async_session_maker_null_pооl


class ReportService:
    def __init__(self, db: DBManager):
        self.db = db

        # Конфигурация отчетов
        self.report_config = {
            "daily_sales": {
                "param_model": SalesDailyParams,
                "db_method": self.db.sales_daily.get_sales_daily,
                "is_summary": False,
            },
            "daily_sales_summary": {
                "param_model": SalesDailyParams,
                "db_method": self.db.sales_daily.get_sales_summary,
                "is_summary": True,
            },
            "sales_by_categories": {
                "param_model": SalesByCategoryDailyParams,
                "db_method": self.db.product_category_daily.get_sales_by_category_daily,
                "is_summary": False,
            },
            "sales_by_categories_summary": {
                "param_model": SalesByCategoryDailyParams,
                "db_method": self.db.product_category_daily.get_sales_by_category_summary,
                "is_summary": True,
            },
            "sales_by_products": {
                "param_model": SalesByProductDailyParams,
                "db_method": self.db.product_category_daily.get_sales_by_product_daily,
                "is_summary": False,
            },
            "sales_by_products_summary": {
                "param_model": SalesByProductDailyParams,
                "db_method": self.db.product_category_daily.get_sales_by_product_summary,
                "is_summary": True,
            },
            "customers": {
                "param_model": SalesByCustomerParams,
                "db_method": self.db.sales_by_customer_daily.get_sales_by_customer_daily,
                "is_summary": False,
            },
            "customers_summary": {
                "param_model": SalesByCustomerParams,
                "db_method": self.db.sales_by_customer_daily.get_sales_by_customer_summary,
                "is_summary": True,
            },
            "payments": {
                "param_model": PaymentsReportParams,
                "db_method": self.db.payments.get_payments_daily,
                "is_summary": False,
            },
            "payments_summary": {
                "param_model": PaymentsReportParams,
                "db_method": self.db.payments.get_payments_summary,
                "is_summary": True,
            },
        }

    async def _save_report_to_csv(self, task_id: str, data, is_summary: bool = False):
        """Универсальный метод сохранения отчета в CSV, работает с одним объектом или списком объектов"""
        if not data:
            print("Нет данных для выбранного периода")
            return None

        os.makedirs("report", exist_ok=True)
        file_path = f"report/{task_id}.csv"

        # Преобразуем в список, если это один объект
        if is_summary and not isinstance(data, list):
            data_list = [data]
        elif isinstance(data, list):
            data_list = data
        else:
            data_list = [data]

        # Преобразуем объекты Pydantic в словари
        dicts = []
        for item in data_list:
            d = item.model_dump() if hasattr(item, "model_dump") else dict(item)
            # округляем числовые значения
            for key, value in d.items():
                if isinstance(value, (int, float)) and value is not None:
                    if key in ["total_amount", "avg_check", "total_payments"]:
                        d[key] = round(float(value), 2)
                    elif key in ["total_quantity", "total_orders", "total_items"]:
                        d[key] = int(value)
            dicts.append(d)

        headers = dicts[0].keys()
        with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, delimiter=";")
            writer.writeheader()
            writer.writerows(dicts)

        return file_path

    async def make_report(self, task_id: str, report_name: str, params: dict):
        """Универсальный метод создания отчета"""
        config = self.report_config.get(report_name)
        if not config:
            raise ValueError(f"Unknown report_name: {report_name}")

        try:
            validated_params = config["param_model"](**params)
        except ValidationError as e:
            print(f"Ошибка валидации параметров: {e}")
            return

        # Получаем данные
        sales_data = await config["db_method"](**validated_params.model_dump())

        # Сохраняем отчет
        file_path = await self._save_report_to_csv(
            task_id, sales_data, config["is_summary"]
        )

        if file_path:
            await self.db.report_task.edit(
                ReportTaskReady(status=Status.ready, result_file=file_path), id=task_id
            )
            await self.db.commit()

    async def make_report_h(self, task_id: str):
        """Основной метод обработки задачи отчета"""
        task = await self.db.report_task.get_one_or_none(id=task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        report_template = await self.db.report_template.get_one_or_none(
            id=task.template_id
        )
        if not report_template:
            raise ValueError(f"Report template with id {task.template_id} not found")

        params = json.loads(task.parameters)
        await self.make_report(task_id, report_template.name, params)


async def get_db_np():
    async with DBManager(session_factory=async_session_maker_null_pооl) as db:
        yield db
