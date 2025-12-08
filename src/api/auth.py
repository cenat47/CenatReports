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


router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post(
    "/register",
    summary="Регистрация нового пользователя",
    description="""Регистрирует нового пользователя в системе.

После успешной регистрации на email отправляется код подтверждения.
Для активации аккаунта необходимо подтвердить email через /verify.

Требования к паролю:
- Минимум 8 символов
- Заглавная латинская буква
- Строчная латинская буква
- Цифра
- Только ASCII символы""",
    responses={
        200: {"description": "Пользователь зарегистрирован, код отправлен на email"},
        400: {"description": "Некорректные данные"},
        409: {"description": "Пользователь уже существует"},
    },
)
async def register(user: UserRequest, db: DBDep):
    return [
        await UserService(db).register_new_user(user),
        "На почту было направлено письмо с кодом для подтверждения, обратитесь к /verify",
    ]


@router.post(
    "/verify",
    summary="Подтверждение email",
    description="""Подтверждает email пользователя с помощью кода из письма.

После успешного подтверждения аккаунт активируется и можно выполнить вход.""",
    responses={
        200: {"description": "Email успешно подтверждён"},
        400: {"description": "Неверный код подтверждения"},
    },
)
async def verify(data: UserVerify, db: DBDep):
    return await UserService(db).verify_user(data)


@router.post(
    "/reverify",
    summary="Повторная отправка кода подтверждения",
    description="""Отправляет новый код подтверждения на email.

Используется если предыдущий код истёк или был утерян.""",
    responses={200: {"description": "Код отправлен (если email существует)"}},
)
async def reverify(data: UserReverify, db: DBDep):
    return await UserService(db).reverify_user(data)


@router.post(
    "/login",
    summary="Вход в систему",
    description="""Аутентификация пользователя по email и паролю.

При успешном входе устанавливаются cookie с access и refresh токенами.

Защита от брутфорса:
- Все попытки входа записываются в аудит-лог

Возвращает токены в теле ответа и устанавливает httpOnly cookies.""",
    response_model=Token,
    responses={
        200: {"description": "Успешный вход, токены установлены"},
        401: {"description": "Неверный email или пароль"},
        429: {"description": "IP заблокирован после множественных неудачных попыток"},
    },
)
async def login(
    data: UserLogin, response: Response, request: Request, db: DBDep
) -> Token:
    user = await UserService(db).authenticate_user(data, request.client.host)
    if not user:
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


@router.post(
    "/logout",
    summary="Выход из системы",
    description="""Завершает текущую сессию пользователя.

Удаляет refresh-токен из базы данных и очищает cookies.
Действие записывается в аудит-лог.""",
    responses={
        200: {"description": "Успешный выход из системы"},
        401: {"description": "Невалидный токен"},
    },
)
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

        session = await db.refresh_token.get_one_or_none(
            refresh_token=refresh_token_uuid
        )
        user_id = session.user_id if session else None

        await UserService(db).logout(refresh_token_uuid, ip_address=request.client.host)

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


@router.post(
    "/refresh",
    summary="Обновление токенов",
    description="""Обновляет access и refresh токены.

Использует refresh-токен из cookies для генерации новой пары токенов.
Старый refresh-токен удаляется, создаётся новый (token rotation).

Действие записывается в аудит-лог.""",
    response_model=Token,
    responses={
        200: {"description": "Токены успешно обновлены"},
        401: {"description": "Невалидный или истёкший refresh-токен"},
    },
)
async def refresh_token(request: Request, response: Response, db: DBDep) -> Token:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise InvalidTokenException
    try:
        refresh_token_uuid = uuid.UUID(refresh_token)

        session = await db.refresh_token.get_one_or_none(
            refresh_token=refresh_token_uuid
        )

        new_token = await UserService(db).refresh_token(
            refresh_token_uuid,
            ip_address=request.client.host,
        )

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


@router.post(
    "/abort",
    summary="Завершение всех сессий",
    description="""Завершает все активные сессии пользователя.

Удаляет все refresh-токены пользователя из базы данных.
Используется для экстренного выхода со всех устройств (например, при подозрении на взлом).

Действие записывается в аудит-лог.""",
    responses={
        200: {"description": "Все сессии завершены"},
        401: {"description": "Невалидный токен"},
    },
)
async def abort_all_sessions(
    response: Response,
    request: Request,
    db: DBDep,
):
    refresh_token = request.cookies.get("refresh_token")

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


@router.post(
    "/me",
    summary="Получение информации о текущем пользователе",
    description="""Возвращает данные авторизованного пользователя.

Требуется валидный access-токен.""",
    responses={
        200: {"description": "Данные пользователя"},
        401: {"description": "Не авторизован"},
    },
)
async def get_me(
    user: get_current_active_user_Dep,
):
    return user
