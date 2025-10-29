from src.repositories.mapper.mappers import UserDataMapper
from src.models.auth.user import UserORM
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    model = UserORM
    mapper = UserDataMapper