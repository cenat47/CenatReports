import uuid

from fastapi import APIRouter, Request, Response

from config import settings
from schemas.auth.refresh_token import Token
from schemas.auth.user import UserLogin, UserRequest, UserReverify, UserVerify
from schemas.security.audit import AuditLogCreate, AuditAction
from services.auth import UserService
from services.audit import AuditService
from src.api.dependencies import DBDep, get_current_active_user_Dep
from src.exceptions import InvalidCredentialsException, InvalidTokenException


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(user: UserRequest, db: DBDep):
    return [
        await UserService(db).register_new_user(user),
        "На почту было направлено письмо с кодом для подтверждения, обратитесь к /verify",
    ]


@router.post("/verify")
async def verify(data: UserVerify, db: DBDep):
    return await UserService(db).verify_user(data)


@router.post("/reverify")
async def reverify(data: UserReverify, db: DBDep):
    return await UserService(db).reverify_user(data)


@router.post("/login")
async def login(
    data: UserLogin, response: Response, request: Request, db: DBDep
) -> Token:
    user = await UserService(db).authenticate_user(data)
    if not user:
        # Аудит неудачного входа
        await AuditService(db).log(
            AuditLogCreate(
                action=AuditAction.LOGIN_FAILED,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                details=f"Failed login attempt for email: {data.email}",
            )
        )
        raise InvalidCredentialsException

    token = await UserService(db).create_token(user.id, request.client.host)

    # Аудит успешного входа
    await AuditService(db).log(
        AuditLogCreate(
            action=AuditAction.LOGIN_SUCCESS,
            user_id=user.id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
        )
    )

    response.set_cookie(
        "access_token",
        token.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        # secure=True,
        samesite="lax",
    )
    response.set_cookie(
        "refresh_token",
        token.refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        # secure=True,
        samesite="lax",
    )
    return token


@router.post("/logout")
async def logout(request: Request, response: Response, db: DBDep):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    if not access_token and not refresh_token:
        return "Вы уже вышли из системы"
    if refresh_token:
        try:
            refresh_token_uuid = uuid.UUID(refresh_token)
        except (ValueError, TypeError):
            raise InvalidTokenException

        # Получаем user_id ДО удаления сессии
        session = await db.refresh_token.get_one_or_none(
            refresh_token=refresh_token_uuid
        )
        user_id = session.user_id if session else None

        await UserService(db).logout(refresh_token_uuid, ip_address=request.client.host)

        # Аудит выхода
        await AuditService(db).log(
            AuditLogCreate(
                action=AuditAction.LOGOUT,
                user_id=user_id,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
            )
        )

        response.delete_cookie("refresh_token")
        if access_token:
            response.delete_cookie("access_token")
        return "Вы успешно вышли из системы"


@router.post("/refresh")
async def refresh_token(request: Request, response: Response, db: DBDep) -> Token:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise InvalidTokenException
    try:
        refresh_token_uuid = uuid.UUID(refresh_token)

        # Получаем сессию для user_id
        session = await db.refresh_token.get_one_or_none(
            refresh_token=refresh_token_uuid
        )

        new_token = await UserService(db).refresh_token(
            refresh_token_uuid,
            ip_address=request.client.host,
        )

        # Аудит обновления токена
        if session:
            await AuditService(db).log(
                AuditLogCreate(
                    action=AuditAction.TOKEN_REFRESH,
                    user_id=session.user_id,
                    ip_address=request.client.host,
                    user_agent=request.headers.get("user-agent"),
                )
            )

    except (ValueError, TypeError):
        raise InvalidTokenException

    response.set_cookie(
        "access_token",
        new_token.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        # secure=True,
        samesite="lax",
    )
    response.set_cookie(
        "refresh_token",
        new_token.refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        # secure=True,
        samesite="lax",
    )
    return new_token


@router.post("/abort")
async def abort_all_sessions(
    response: Response,
    request: Request,
    db: DBDep,
):
    refresh_token = request.cookies.get("refresh_token")

    # Получаем user_id ДО удаления сессий
    if refresh_token:
        try:
            refresh_token_uuid = uuid.UUID(refresh_token)
            session = await db.refresh_token.get_one_or_none(
                refresh_token=refresh_token_uuid
            )
            user_id = session.user_id if session else None
        except (ValueError, TypeError):
            user_id = None
    else:
        user_id = None

    await UserService(db).abort_all_sessions(refresh_token, request.client.host)

    # Аудит завершения всех сессий
    if user_id:
        await AuditService(db).log(
            AuditLogCreate(
                action=AuditAction.ABORT_ALL_SESSIONS,
                user_id=user_id,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
            )
        )

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "All sessions was aborted"}


@router.post("/me")
async def get_me(
    user: get_current_active_user_Dep,
):
    return user
