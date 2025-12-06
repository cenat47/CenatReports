from fastapi import APIRouter, Request
from services.admin import AdminService
from services.audit import AuditService
from schemas.auth.user import UserRoleUpdate, UserRoleUpdateConfirm
from schemas.security.audit import AuditLogCreate, AuditAction
from src.api.dependencies import DBDep, get_current_active_admin_Dep

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/status")
async def admin_status(current_user: get_current_active_admin_Dep):
    return {"status": "Доступ администратора предоставлен"}


@router.patch("/users/role/")
async def update_user_role(
    current_user: get_current_active_admin_Dep,
    db: DBDep,
    request: Request,
    payload: UserRoleUpdate,
):
    # Получаем пользователя по email из payload
    target_user = await db.user.get_one_or_none(email=payload.email)

    result = await AdminService(db).update_user_role(current_user, payload)

    # Аудит запроса на изменение роли
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


@router.patch("/users/role/confirm")
async def confirm_user_role_update(
    current_user: get_current_active_admin_Dep,
    db: DBDep,
    request: Request,
    payload: UserRoleUpdateConfirm,
):
    # Получаем пользователя по email из payload и старую роль ДО изменения
    target_user = await db.user.get_one_or_none(email=payload.email)
    old_role = target_user.role if target_user else None

    result = await AdminService(db).confirm_user_role_update(current_user, payload)

    # Аудит подтверждения изменения роли
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
