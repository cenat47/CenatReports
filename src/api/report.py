import uuid
from fastapi import APIRouter, Body
from fastapi.responses import FileResponse

from api.dependencies import DBDep
from exceptions import (
    ObjectIsNotExistsException,
    PermissionDeniedException,
    ReportIsNotReady,
)
from schemas.report.report_task import ReportRequest, ReportTaskStatus
from services.report import ReportService
from src.schemas.report.sales_daily import SalesDailyParams
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
        ...,
        example={
            "report_name": "daily_sales",
            "parameters": {
                "date_from": "2023-11-16",
                "date_to": "2025-11-15",
            },
        },
    ),
):
    return await ReportService(db).generate_report_task(
        user_id=user.id, report_name=request.report_name, parameters=request.parameters
    )


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
