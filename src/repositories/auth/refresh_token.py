from src.models.auth.refresh_token import RefreshTokenORM
from src.repositories.base import BaseRepository
from src.repositories.mapper.mappers import RefreshTokenDataMapper


class RefreshTokenRepository(BaseRepository):
    model = RefreshTokenORM
    mapper = RefreshTokenDataMapper
