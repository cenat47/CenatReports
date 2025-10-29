from src.repositories.mapper.mappers import RefreshTokenDataMapper
from src.models.auth.refresh_token import RefreshTokenORM
from src.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository):
    model = RefreshTokenORM
    mapper = RefreshTokenDataMapper