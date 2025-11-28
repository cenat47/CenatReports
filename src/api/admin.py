import random
from src.init import redis_manager
from src.tasks.email_tasks import send_role_change_email_task
from fastapi import APIRouter
from schemas.auth.user import UserRoleEdit, UserRoleUpdate, UserRoleUpdateConfirm
from src.api.dependencies import DBDep, get_current_active_admin_Dep
from src.exceptions import InvalidVerificationCodeException, PermissionDeniedException, UserNotFoundException, UserSelfRoleUpdateException
router = APIRouter(prefix="/admin", tags=["admin"])  

@router.get("/status")
async def admin_status(current_user: get_current_active_admin_Dep):
    return {"status": "Доступ администратора предоставлен"}

@router.patch("/users/role/")
async def update_user_role(current_user: get_current_active_admin_Dep, db: DBDep, payload: UserRoleUpdate):
    
    user = await db.user.get_one_or_none(email=payload.email)
    if not user:
        raise UserNotFoundException 
    
    if user.id == current_user.id:
        raise UserSelfRoleUpdateException
    if user.role == "superadmin":
        raise PermissionDeniedException
    if user.role == "admin" and current_user.role != "superadmin":
        raise PermissionDeniedException
    if payload.new_role == "superadmin":
        raise PermissionDeniedException
    if payload.new_role == "admin" and current_user.role != "superadmin":
        raise PermissionDeniedException
    if user.role == payload.new_role:
        return {"message": "Роль уже установлена", "user_id": user.id, "role": user.role}
    
    if user.role == payload.new_role:
        return {
            "message": "Роль уже установлена",
            "user_email": user.email,
            "role": user.role
        }
    
    code = f"{random.randint(0, 999999):06d}"

    redis_key = f"role_change:{current_user.email}:{payload.email}:{payload.new_role}"
    await redis_manager.set(redis_key, code, expire=600)

    send_role_change_email_task.delay(
        current_user.email,
        payload.email,
        payload.new_role,
        code
    )

    return {"message": "Код подтверждения отправлен на email"}

@router.patch("/users/role/confirm")
async def confirm_user_role_update(
    current_user: get_current_active_admin_Dep,
    db: DBDep,
    payload: UserRoleUpdateConfirm
):
    redis_key = f"role_change:{current_user.email}:{payload.email}:{payload.new_role}"
    code = await redis_manager.get(redis_key)

    if not code or code != payload.code:
        raise InvalidVerificationCodeException

    target_user = await db.user.get_one_or_none(email=payload.email)
    if not target_user:
        raise UserNotFoundException

    await db.user.edit(
    data=UserRoleEdit(role=payload.new_role),
    email=payload.email
)
    await db.commit()

    await redis_manager.delete(redis_key)

    return {
        "message": "Роль успешно изменена",
        "user_email": payload.email,
        "new_role": payload.new_role
    }

