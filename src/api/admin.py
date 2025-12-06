from fastapi import APIRouter, Request
from services.admin import AdminService
from services.audit import AuditService
from schemas.auth.user import UserRoleUpdate, UserRoleUpdateConfirm
from schemas.security.audit import AuditLogCreate, AuditAction
from src.api.dependencies import DBDep, get_current_active_admin_Dep


router = APIRouter(prefix="/admin", tags=["Администрирование"])


@router.get(
    "/status",
    summary="Проверка доступа администратора",
    description="Проверяет, что текущий пользователь имеет права администратора",
    responses={
        200: {
            "description": "Доступ подтверждён",
            "content": {
                "application/json": {
                    "example": {"status": "Доступ администратора предоставлен"}
                }
            }
        },
        403: {"description": "Недостаточно прав"}
    }
)
async def admin_status(current_user: get_current_active_admin_Dep):
    return {"status": "Доступ администратора предоставлен"}


@router.patch(
    "/users/role/",
    summary="Запрос на изменение роли пользователя",
    description="""Создаёт запрос на изменение роли пользователя с отправкой кода подтверждения на email.

Процесс изменения роли:
- Администратор отправляет запрос с email пользователя и новой ролью
- На email администратора отправляется код подтверждения
- Администратор подтверждает изменение через /users/role/confirm с кодом

Доступные роли: user, manager, admin

Действие записывается в аудит-лог.""",
    responses={
        200: {
            "description": "Запрос создан, код отправлен на email",
            "content": {
                "application/json": {
                    "example": {"message": "Код подтверждения отправлен на почту пользователя"}
                }
            }
        },
        403: {"description": "Недостаточно прав или попытка изменить свою роль"},
        404: {"description": "Пользователь не найден"}
    }
)
async def update_user_role(
    current_user: get_current_active_admin_Dep,
    db: DBDep,
    request: Request,
    payload: UserRoleUpdate,
):
    target_user = await db.user.get_one_or_none(email=payload.email)

    result = await AdminService(db).update_user_role(current_user, payload)

    await AuditService(db).log(
        AuditLogCreate(
            action=AuditAction.ROLE_CHANGE_REQUEST,
            user_id=current_user.id,
            table_name="users",
            record_id=str(target_user.id) if target_user else payload.email,
            new_values={
                "requested_role": payload.new_role,
                "target_email": payload.email,
            },
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            details=f"Admin {current_user.email} requested role change for user {payload.email}",
        )
    )

    return result


@router.patch(
    "/users/role/confirm",
    summary="Подтверждение изменения роли",
    description="""Подтверждает изменение роли пользователя с помощью кода из email.

Требуется код подтверждения, который был отправлен на email администратора после создания запроса.

Изменение записывается в аудит с указанием старой и новой роли.""",
    responses={
        200: {
            "description": "Роль успешно изменена",
            "content": {
                "application/json": {
                    "example": {"message": "Роль пользователя успешно изменена"}
                }
            }
        },
        400: {"description": "Неверный код подтверждения"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Пользователь не найден"}
    }
)
async def confirm_user_role_update(
    current_user: get_current_active_admin_Dep,
    db: DBDep,
    request: Request,
    payload: UserRoleUpdateConfirm,
):
    target_user = await db.user.get_one_or_none(email=payload.email)
    old_role = target_user.role if target_user else None

    result = await AdminService(db).confirm_user_role_update(current_user, payload)

    await AuditService(db).log(
        AuditLogCreate(
            action=AuditAction.ROLE_CHANGE_CONFIRM,
            user_id=current_user.id,
            table_name="users",
            record_id=str(target_user.id) if target_user else payload.email,
            old_values={"role": old_role, "target_email": payload.email},
            new_values={"role": payload.new_role, "target_email": payload.email},
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            details=f"Admin {current_user.email} confirmed role change for user {payload.email}",
        )
    )

    return result
