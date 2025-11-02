from src.models.auth.user import UserORM
from src.repositories.base import BaseRepository
from src.repositories.mapper.mappers import UserDataMapper


class UserRepository(BaseRepository):
    model = UserORM
    mapper = UserDataMapper
