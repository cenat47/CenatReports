import uuid
from fastapi import APIRouter, Depends, Response, Request, status

from config import settings
from src.exceptions import InvalidCredentials, InvalidTokenException
from schemas.auth.refresh_token import RefreshToken, Token
from schemas.auth.user import User, UserAdd, UserLogin, UserRequest
from services.auth import UserService
from src.api.dependencies import DBDep, get_current_active_user, get_current_active_user_Dep
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(
    user: UserRequest, db: DBDep
) ->User:
    return await UserService(db).register_new_user(user)


@router.post("/login")
async def login(
    data: UserLogin,
    response: Response,
    request: Request,
    db: DBDep
) -> Token:
    user = await UserService(db).authenticate_user(data)
    if not user:
        raise InvalidCredentials
    token = await UserService(db).create_token(user.id,request.client.host)
    response.set_cookie(
        'access_token',
        token.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        # secure=True,
        samesite="lax"  
    )
    response.set_cookie(
        'refresh_token',
        token.refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        # secure=True,
        samesite="lax"
    )
    return token


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: DBDep
):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    if not access_token and not refresh_token:
        return "Вы уже вышли из системы"
    if refresh_token:
        try:
            refresh_token = uuid.UUID(refresh_token)
        except (ValueError, TypeError):
            raise InvalidTokenException
        await UserService(db).logout(request.cookies.get('refresh_token'), ip_address=request.client.host)
        response.delete_cookie('refresh_token')
        if  access_token:
            response.delete_cookie('access_token')
        return "Вы успешно вышли из системы"


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    db: DBDep
) -> Token:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise InvalidTokenException
    try:
        new_token = await UserService(db).refresh_token(
            uuid.UUID(request.cookies.get("refresh_token")), ip_address = request.client.host
        )
    except (ValueError, TypeError):
        raise InvalidTokenException
    response.set_cookie(
        'access_token',
        new_token.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        # secure=True,
        samesite="lax"
    )
    response.set_cookie(
        'refresh_token',
        new_token.refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        # secure=True,
        samesite="lax"
    )
    return new_token

@router.post("/abort")
async def abort_all_sessions(
    response: Response,
    request: Request,
    db: DBDep,
):
    refresh_token = request.cookies.get("refresh_token")
    await UserService(db).abort_all_sessions(refresh_token, request.client.host)
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return {"message": "All sessions was aborted"}