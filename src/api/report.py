import uuid
from fastapi import APIRouter, Body
from fastapi.responses import FileResponse

from api.dependencies import DBDep
from exceptions import (
    ObjectIsNotExistsException,
    PermissionDeniedException,
    ReportIsNotReady,
    ReportParametersValidationException,
    ReportParametersValidationHTTPException,
    TempelateIsNotExistsException,
)
from schemas.report.report_task import ReportRequest, ReportTaskStatus
from services.report import ReportServiceS
from src.api.dependencies import (
    get_current_active_manager_Dep,
    get_current_active_user_Dep,
)

router = APIRouter(prefix="/report", tags=["report"])


@router.post("/generate")
async def generate_report(
    db: DBDep,
    user: get_current_active_manager_Dep,
    request: ReportRequest = Body(
        openapi_examples={
            # === DAILY SALES ===
            "daily_sales": {
                "summary": "Daily Sales Report",
                "value": {
                    "report_name": "daily_sales",
                    "parameters": {"date_from": "2023-11-16", "date_to": "2025-11-15"},
                },
            },
            "daily_sales_summary": {
                "summary": "Daily Sales Report Summary",
                "value": {
                    "report_name": "daily_sales_summary",
                    "parameters": {"date_from": "2023-11-16", "date_to": "2025-11-15"},
                },
            },
            # === CATEGORY REPORTS ===
            "sales_by_category_daily": {
                "summary": "Sales by Category — Daily Details",
                "value": {
                    "report_name": "sales_by_categories",
                    "parameters": {
                        "date_from": "2025-01-01",
                        "date_to": "2025-01-31",
                        "category_id": 3,
                        "top": 10,
                    },
                },
            },
            "sales_by_category_summary": {
                "summary": "Sales by Category — Summary",
                "value": {
                    "report_name": "sales_by_categories_summary",
                    "parameters": {
                        "date_from": "2025-01-01",
                        "date_to": "2025-01-31",
                        "category_id": 3,
                        "top": 5,
                    },
                },
            },
            # === PRODUCT REPORTS ===
            "sales_by_product_daily": {
                "summary": "Sales by Product — Daily Details",
                "value": {
                    "report_name": "sales_by_products",
                    "parameters": {
                        "date_from": "2025-01-01",
                        "date_to": "2025-01-31",
                        "product_id": 15,
                        "top": 5,
                    },
                },
            },
            "sales_by_product_summary": {
                "summary": "Sales by Product — Summary",
                "value": {
                    "report_name": "sales_by_products_summary",
                    "parameters": {
                        "date_from": "2025-01-01",
                        "date_to": "2025-01-31",
                        "product_id": 15,
                        "top": 5,
                    },
                },
            },
            # === CATEGORY TOP ===
            "sales_by_category_top": {
                "summary": "Top Categories by sales",
                "value": {
                    "report_name": "sales_by_categories_summary",
                    "parameters": {
                        "date_from": "2025-01-01",
                        "date_to": "2025-01-31",
                        "top": 5,
                    },
                },
            },
            # === PRODUCT TOP ===
            "sales_by_product_top": {
                "summary": "Top Products by sales",
                "value": {
                    "report_name": "sales_by_products_summary",
                    "parameters": {
                        "date_from": "2025-01-01",
                        "date_to": "2025-01-31",
                        "top": 5,
                    },
                },
            },
            "sales_by_customer_daily": {
                "summary": "Sales by Customer — Daily Details",
                "value": {
                    "report_name": "customers",
                    "parameters": {
                        "date_from": "2025-01-01",
                        "date_to": "2025-01-31",
                        "customer_id": 301,
                    },
                },
            },
            "sales_by_customer_summary": {
                "summary": "Top Customers by sales",
                "value": {
                    "report_name": "customers_summary",
                    "parameters": {
                        "date_from": "2025-01-01",
                        "date_to": "2025-01-31",
                        "top": 10,
                    },
                },
            },
            "payments_daily": {
                "summary": "Payments by Method — Daily",
                "value": {
                    "report_name": "payments",
                    "parameters": {
                        "date_from": "2025-01-01",
                        "date_to": "2025-01-31",
                        "payment_method": "card",
                    },
                },
            },
            "payments_summary": {
                "summary": "Payments by Method — Summary",
                "value": {
                    "report_name": "payments_summary",
                    "parameters": {"date_from": "2025-01-01", "date_to": "2025-01-31"},
                },
            },
            "payments_top": {
                "summary": "Top Payment Methods",
                "value": {
                    "report_name": "payments_summary",
                    "parameters": {
                        "date_from": "2025-01-01",
                        "date_to": "2025-01-31",
                        "top": 2,
                    },
                },
            },
        }
    ),
):
    try:
        return await ReportServiceS(db).generate_report_task(
            user_id=user.id,
            report_name=request.report_name,
            parameters=request.parameters,
        )
    except ValueError:
        raise TempelateIsNotExistsException
    except ReportParametersValidationException:
        raise ReportParametersValidationHTTPException


@router.get("/status/{task_id}", response_model=ReportTaskStatus)
async def get_report_status(
    task_id: uuid.UUID, db: DBDep, current_user: get_current_active_user_Dep
):
    task = await db.report_task.get_one_or_none(id=task_id)
    if task is None:
        raise ObjectIsNotExistsException

    # Проверяем, что задача принадлежит текущему пользователю
    if task.user_id != current_user.id and current_user.role not in [
        "admin",
        "superadmin",
    ]:
        raise PermissionDeniedException

    status = task.status
    file_path = task.result_file
    error_message = task.error_message

    return ReportTaskStatus(
        task_id=task_id,
        status=status,
        result_file=file_path,
        error_message=error_message,
    )


@router.get("/download/{task_id}")
async def download_report(
    task_id: uuid.UUID, db: DBDep, current_user: get_current_active_user_Dep
):
    # Получаем задачу
    task = await db.report_task.get_one_or_none(id=task_id)
    if not task:
        raise ObjectIsNotExistsException

    # Проверяем права пользователя
    if task.user_id != current_user.id and current_user.role not in [
        "admin",
        "superadmin",
    ]:
        raise PermissionDeniedException

    # Проверяем, готов ли файл
    if task.status != "ready" or not task.result_file:
        raise ReportIsNotReady

    # Отдаём файл
    return FileResponse(
        path=task.result_file, filename=f"report_{task_id}.csv", media_type="text/csv"
    )


@router.get("/tasks/me")
async def get_my_report(current_user: get_current_active_user_Dep, db: DBDep):
    return await db.report_task.get_all(user_id=current_user.id)


@router.get("/info")
async def get_all_template(db: DBDep):
    return await db.report_template.get_all()
