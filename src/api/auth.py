from fastapi import APIRouter, Depends, Response, Request, status

from schemas.auth.user import User, UserAdd, UserRequest
from services.auth import UserService
from src.api.dependencies import DBDep
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(
    user: UserRequest, db: DBDep
) ->User:
    return await UserService(db).register_new_user(user)


# @router.post("/login")
# async def login(
#     response: Response,
#     credentials: OAuth2PasswordRequestForm = Depends()
# ) -> Token:
#     user = await AuthService.authenticate_user(credentials.username, credentials.password)
#     if not user:
#         raise InvalidCredentialsException
#     token = await AuthService.create_token(user.id)
#     response.set_cookie(
#         'access_token',
#         token.access_token,
#         max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
#         httponly=True
#     )
#     response.set_cookie(
#         'refresh_token',
#         token.refresh_token,
#         max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 30 * 24 * 60,
#         httponly=True
#     )
#     return token


# @router.post("/logout")
# async def logout(
#     request: Request,
#     response: Response,
#     user: UserModel = Depends(get_current_active_user),
# ):
#     response.delete_cookie('access_token')
#     response.delete_cookie('refresh_token')

#     await AuthService.logout(request.cookies.get('refresh_token'))
#     return {"message": "Logged out successfully"}


# @router.post("/refresh")
# async def refresh_token(
#     request: Request,
#     response: Response
# ) -> Token:
#     new_token = await AuthService.refresh_token(
#         uuid.UUID(request.cookies.get("refresh_token"))
#     )

#     response.set_cookie(
#         'access_token',
#         new_token.access_token,
#         max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
#         httponly=True,
#     )
#     response.set_cookie(
#         'refresh_token',
#         new_token.refresh_token,
#         max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 30 * 24 * 60,
#         httponly=True,
#     )
#     return new_token