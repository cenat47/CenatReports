from datetime import datetime
from src.exceptions import ObjectAlreadyExistsException, UserAlreadyExists
from schemas.auth.user import User, UserAdd, UserRequest
from src.services.base import BaseService
from src.utils.password_utils import get_password_hash

class UserService(BaseService):
    async def register_new_user(self, user: UserRequest) -> User:
        password_hash = get_password_hash(user.password)
        useradd = UserAdd(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=True,
            registered_at=datetime.utcnow(),
            password_hash=password_hash
        )
        try:
            db_user = await self.db.user.add(useradd)
            await self.db.commit()
        except ObjectAlreadyExistsException:
            raise UserAlreadyExists()
        return db_user


