from typing import Annotated
import uuid

from fastapi import Depends, Cookie, Request

from src.schemas.auth.user import User
from src.services.auth import UserService
from src.exceptions import InvalidTokenException, UserNotActiveExc
from src.utils.db_manager import DBManager
from src.database import async_session_maker
from jose import jwt
from config import settings


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


async def get_current_user(
    db: DBDep,
    request: Request
):
    token = request.cookies.get("access_token")
    if token is None:
        raise InvalidTokenException

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidTokenException
    except Exception:
        raise InvalidTokenException

    current_user = await UserService(db).get_user(uuid.UUID(user_id))
    return current_user


async def get_current_active_user(
    current_user: str = Depends(get_current_user)
):
    if not current_user.is_active:
        raise UserNotActiveExc
    return current_user


get_current_active_user_Dep = Annotated[
    User,
    Depends(get_current_active_user)
]
