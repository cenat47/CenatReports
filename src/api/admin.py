import random
from services.admin import AdminService
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
    return await AdminService(db).update_user_role(current_user, payload)

@router.patch("/users/role/confirm")
async def confirm_user_role_update(
    current_user: get_current_active_admin_Dep,
    db: DBDep,
    payload: UserRoleUpdateConfirm
):
    return await AdminService(db).confirm_user_role_update(current_user, payload)
