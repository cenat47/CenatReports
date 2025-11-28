import uuid
from typing import Annotated

from fastapi import Depends, Request
from jose import JWTError, jwt

from src.config import settings
from src.database import async_session_maker
from src.exceptions import (
    EmailNotVerifiedException,
    InvalidTokenException,
    PermissionDeniedException,
    UserNotActiveException,
)
from src.schemas.auth.user import User, UserRole
from src.services.auth import UserService
from src.utils.db_manager import DBManager


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


async def get_current_user(db: DBDep, request: Request):
    token = request.cookies.get("access_token")
    if token is None:
        raise InvalidTokenException

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidTokenException
    except JWTError:
        raise InvalidTokenException

    current_user = await UserService(db).get_user(uuid.UUID(user_id))
    return current_user


async def check_active(user: User):
    if not user.is_active:
        raise UserNotActiveException
    if not user.is_verified:
        raise EmailNotVerifiedException


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    await check_active(current_user)
    return current_user


async def get_current_active_manager(current_user: User = Depends(get_current_user)):
    await check_active(current_user)
    if current_user.role == UserRole.user:
        raise PermissionDeniedException
    return current_user


async def get_current_active_admin(current_user: User = Depends(get_current_user)):
    await check_active(current_user)
    if current_user.role in [UserRole.user, UserRole.manager]:
        raise PermissionDeniedException
    return current_user


async def get_current_active_superadmin(current_user: User = Depends(get_current_user)):
    await check_active(current_user)
    if current_user.role != UserRole.superadmin:
        raise PermissionDeniedException
    return current_user


get_current_active_user_Dep = Annotated[User, Depends(get_current_active_user)]

get_current_active_manager_Dep = Annotated[User, Depends(get_current_active_manager)]

get_current_active_admin_Dep = Annotated[User, Depends(get_current_active_admin)]

get_current_active_superadmin_Dep = Annotated[
    User, Depends(get_current_active_superadmin)
]
