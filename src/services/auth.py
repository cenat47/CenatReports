import random
import uuid
from datetime import datetime, timedelta, timezone
from src.init import redis_manager
from jose import jwt
from src.config import settings
from src.exceptions import (
    ExpiredTokenException,
    InvalidTokenException,
    InvalidVerificationCodeException,
    ObjectAlreadyExistsException,
    UserAlreadyExistsException,
    UserNotFoundException,
    WeakPasswordException,
)
from src.schemas.auth.refresh_token import RefreshTokenAdd, Token
from src.schemas.auth.user import (
    LastLoginUpdate,
    User,
    UserAdd,
    UserLogin,
    UserRequest,
    UserReverify,
    UserVerify,
    VerifyStatus,
)
from src.services.base import BaseService
from src.utils.password_utils import get_password_hash, is_valid_password, validate_password_strength
from src.tasks.email_tasks import send_verification_email_task


class UserService(BaseService):
    async def register_new_user(self, user: UserRequest) -> User:
        is_valid, error_message = validate_password_strength(user.password)
        if not is_valid:
            raise WeakPasswordException(detail=error_message)
        password_hash = get_password_hash(user.password)
        useradd = UserAdd(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=True,
            is_verified=False,
            password_hash=password_hash,
        )
        try:
            db_user = await self.db.user.add(useradd)
            await self.db.commit()
        except ObjectAlreadyExistsException:
            raise UserAlreadyExistsException()
        code = f"{random.randint(0, 999999):06d}"
        redis_key = f"email_verification:{user.email}"
        await redis_manager.set(key=redis_key, value=code, expire=600)
        send_verification_email_task.delay(user.email, code)
        return db_user

    async def verify_user(self, data: UserVerify) -> str:
        key = f"email_verification:{data.email}"
        code = await redis_manager.get(key)
        if not code:
            raise InvalidVerificationCodeException
        if code != data.code:
            raise InvalidVerificationCodeException
        await self.db.user.edit(data=VerifyStatus(is_verified=True), email=data.email)
        await self.db.commit()
        await redis_manager.delete(key)
        return "Email успешно подтверждён"

    async def reverify_user(self, data: UserReverify) -> str:
        email = data.email
        user = await self.db.user.get_one_or_none(email=email)
        if not user or user.is_verified:
            return "Если email существует, код подтверждения отправлен"
        code = f"{random.randint(0, 999999):06d}"
        key = f"email_verification:{email}"
        await redis_manager.set(key=key, value=code, expire=600)
        send_verification_email_task.delay(email, code)
        return "Если email существует, код подтверждения отправлен"

    async def authenticate_user(self, data: UserLogin):
        db_user = await self.db.user.get_one_or_none(email=data.email)
        if db_user and is_valid_password(data.password, db_user.password_hash):
            await self.db.user.edit(
                data=LastLoginUpdate(last_login_at=datetime.now(timezone.utc)),
                id=db_user.id,
            )
            return db_user
        return None

    async def create_token(self, user_id: uuid.UUID, ip_address: str) -> Token:
        access_token = self._create_access_token(user_id)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = self._create_refresh_token()
        expires_at = datetime.now(timezone.utc) + refresh_token_expires
        await self.db.refresh_token.add(
            RefreshTokenAdd(
                user_id=user_id,
                refresh_token=refresh_token,
                expires_at=expires_at,
                ip_address=ip_address,
            )
        )
        await self.db.commit()
        return Token(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    def _create_refresh_token(self) -> str:
        return uuid.uuid4()

    def _create_access_token(self, user_id: uuid.UUID) -> str:
        to_encode = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    async def get_user(self, user_id: uuid.UUID):
        db_user = await self.db.user.get_one_or_none(id=user_id)
        if db_user is None:
            raise UserNotFoundException
        return db_user

    async def logout(self, token: uuid.UUID, ip_address: str) -> None:
        refresh_token = await self.db.refresh_token.get_one_or_none(refresh_token=token)
        if not refresh_token:
            raise InvalidTokenException
        if refresh_token.ip_address != ip_address:
            raise InvalidTokenException
        await self.db.refresh_token.delete(id=refresh_token.id)
        await self.db.commit()

    async def refresh_token(self, token: uuid.UUID, ip_address: str) -> Token:
        old_token = await self.db.refresh_token.get_one_or_none(refresh_token=token)
        if old_token is None:
            raise InvalidTokenException
        if datetime.now(timezone.utc) >= old_token.expires_at:
            await self.db.refresh_token.delete(id=old_token.id)
            raise ExpiredTokenException
        if old_token.ip_address != ip_address:
            raise InvalidTokenException
        user = await self.db.user.get_one_or_none(id=old_token.user_id)
        if user is None:
            raise InvalidTokenException
        access_token = self._create_access_token(old_token.user_id)
        new_refresh_token = self._create_refresh_token()
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        expires_at = datetime.now(timezone.utc) + refresh_token_expires
        await self.db.refresh_token.add(
            RefreshTokenAdd(
                user_id=old_token.user_id,
                refresh_token=new_refresh_token,
                expires_at=expires_at,
                ip_address=ip_address,
            )
        )
        await self.db.refresh_token.delete(id=old_token.id)
        await self.db.commit()
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )

    async def abort_all_sessions(self, token: uuid.UUID, ip_address: str):
        session = await self.db.refresh_token.get_one_or_none(refresh_token=token)
        if not session:
            raise InvalidTokenException
        if session.ip_address != ip_address:
            raise InvalidTokenException
        await self.db.refresh_token.delete(user_id=session.user_id)
        await self.db.commit()
