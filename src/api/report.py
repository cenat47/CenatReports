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


router = APIRouter(prefix="/report", tags=["Отчёты"])


@router.post(
    "/generate",
    summary="Создание задачи на генерацию отчёта",
    description="""Создаёт фоновую задачу на генерацию отчёта.

Отчёт генерируется асинхронно через Celery и может занять некоторое время.
После создания задачи используйте /status/{task_id} для проверки готовности.

Доступные типы отчётов: /report/info

Требуется роль: manager, admin

Действие записывается в аудит-лог.""",
    responses={
        200: {
            "description": "Задача создана",
            "content": {
                "application/json": {
                    "example": {
                        "task_id": "123e4567-e89b-12d3-a456-426614174000",
                        "status": "pending",
                    }
                }
            },
        },
        422: {"description": "Некорректные параметры отчёта"},
        403: {"description": "Недостаточно прав (требуется роль manager)"},
        404: {"description": "Шаблон отчёта не найден"},
    },
)
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


@router.get(
    "/status/{task_id}",
    summary="Проверка статуса генерации отчёта",
    description="""Возвращает текущий статус задачи на генерацию отчёта.

Возможные статусы:
- pending - задача в очереди или выполняется
- ready - отчёт готов к скачиванию
- error - произошла ошибка

Пользователь может проверять только свои задачи.
Администраторы могут проверять любые задачи.

Попытки доступа к чужим отчётам записываются в аудит-лог.""",
    response_model=ReportTaskStatus,
    responses={
        200: {"description": "Статус задачи"},
        403: {"description": "Попытка доступа к чужому отчёту"},
        404: {"description": "Задача не найдена"},
    },
)
async def get_report_status(
    task_id: uuid.UUID,
    db: DBDep,
    current_user: get_current_active_user_Dep,
    request: Request,
):
    task = await db.report_task.get_one_or_none(id=task_id)
    if task is None:
        raise ObjectIsNotExistsException

    if task.user_id != current_user.id and current_user.role not in [
        "admin",
        "superadmin",
    ]:
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


@router.get(
    "/download/{task_id}",
    summary="Скачивание готового отчёта",
    description="""Скачивает сгенерированный отчёт в формате CSV.

Отчёт должен иметь статус 'ready'.
Пользователь может скачивать только свои отчёты.
Администраторы могут скачивать любые отчёты.

Безопасность:
- Все скачивания записываются в аудит-лог
- Попытки несанкционированного доступа фиксируются
- Файлы хранятся вне web-root директории""",
    responses={
        200: {"description": "CSV файл с отчётом", "content": {"text/csv": {}}},
        403: {"description": "Попытка скачать чужой отчёт"},
        404: {"description": "Отчёт не найден"},
    },
)
async def download_report(
    task_id: uuid.UUID,
    db: DBDep,
    current_user: get_current_active_user_Dep,
    request: Request,
):
    task = await db.report_task.get_one_or_none(id=task_id)
    if not task:
        raise ObjectIsNotExistsException

    if task.user_id != current_user.id and current_user.role not in [
        "admin",
        "superadmin",
    ]:
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

    if task.status != "ready" or not task.result_file:
        raise ReportIsNotReady

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

    return FileResponse(
        path=task.result_file, filename=f"report_{task_id}.csv", media_type="text/csv"
    )


@router.get(
    "/tasks/me",
    summary="Список моих задач на генерацию отчётов",
    description="""Возвращает список всех задач на генерацию отчётов текущего пользователя.

Включает задачи со всеми статусами: pending, ready, error.""",
    responses={
        200: {"description": "Список задач пользователя"},
        401: {"description": "Не авторизован"},
    },
)
async def get_my_report(current_user: get_current_active_user_Dep, db: DBDep):
    return await db.report_task.get_all(user_id=current_user.id)


@router.get(
    "/info",
    summary="Список доступных шаблонов отчётов",
    description="""Возвращает список всех доступных шаблонов отчётов с описанием.

Включает информацию о:
- Названии отчёта
- Описании
- Требуемых параметрах
- Ролях, которым доступен отчёт""",
    responses={200: {"description": "Список шаблонов отчётов"}},
)
async def get_all_template(db: DBDep):
    return await db.report_template.get_all()
