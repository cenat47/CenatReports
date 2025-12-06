import uuid
from fastapi import APIRouter, Body, Request
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
from schemas.security.audit import AuditLogCreate, AuditAction
from services.report import ReportServiceS
from services.audit import AuditService
from src.api.dependencies import (
    get_current_active_manager_Dep,
    get_current_active_user_Dep,
)
from src.schemas.report.example import REPORT_EXAMPLES

router = APIRouter(prefix="/report", tags=["report"])


@router.post("/generate")
async def generate_report(
    db: DBDep,
    user: get_current_active_manager_Dep,
    http_request: Request,
    request: ReportRequest = Body(openapi_examples=REPORT_EXAMPLES),
):
    try:
        task = await ReportServiceS(db).generate_report_task(
            user_id=user.id,
            report_name=request.report_name,
            parameters=request.parameters,
        )

        # Аудит создания задачи на генерацию отчёта
        await AuditService(db).log(
            AuditLogCreate(
                action=AuditAction.REPORT_GENERATE,
                user_id=user.id,
                table_name="report_tasks",
                record_id=str(task.id),
                new_values={
                    "report_name": request.report_name,
                    "parameters": request.parameters,
                },
                ip_address=http_request.client.host,
                user_agent=http_request.headers.get("user-agent"),
                details=f"User {user.email} requested report: {request.report_name}",
            )
        )

        return {"task_id": task.id, "status": "pending"}

    except ValueError:
        raise TempelateIsNotExistsException
    except ReportParametersValidationException:
        raise ReportParametersValidationHTTPException


@router.get("/status/{task_id}", response_model=ReportTaskStatus)
async def get_report_status(
    task_id: uuid.UUID,
    db: DBDep,
    current_user: get_current_active_user_Dep,
    request: Request,
):
    task = await db.report_task.get_one_or_none(id=task_id)
    if task is None:
        raise ObjectIsNotExistsException

    # Проверяем, что задача принадлежит текущему пользователю
    if task.user_id != current_user.id and current_user.role not in [
        "admin",
        "superadmin",
    ]:
        # Аудит попытки несанкционированного доступа
        await AuditService(db).log(
            AuditLogCreate(
                action=AuditAction.ACCESS_DENIED,
                user_id=current_user.id,
                table_name="report_tasks",
                record_id=str(task_id),
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                details=f"User {current_user.email} tried to access report status owned by user_id={task.user_id}",
            )
        )
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
    task_id: uuid.UUID,
    db: DBDep,
    current_user: get_current_active_user_Dep,
    request: Request,
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
        # Аудит попытки несанкционированного доступа
        await AuditService(db).log(
            AuditLogCreate(
                action=AuditAction.ACCESS_DENIED,
                user_id=current_user.id,
                table_name="report_tasks",
                record_id=str(task_id),
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                details=f"User {current_user.email} tried to download report owned by user_id={task.user_id}",
            )
        )
        raise PermissionDeniedException

    # Проверяем, готов ли файл
    if task.status != "ready" or not task.result_file:
        raise ReportIsNotReady

    # Аудит успешного скачивания отчёта
    await AuditService(db).log(
        AuditLogCreate(
            action=AuditAction.REPORT_DOWNLOAD,
            user_id=current_user.id,
            table_name="report_tasks",
            record_id=str(task_id),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            details=f"User {current_user.email} downloaded report {task_id}",
        )
    )

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
