from src.models.commerce.category import CategoryORM
from src.repositories.base import BaseRepository
from src.repositories.mapper.mappers import CategoryDataMapper


class CategoryRepository(BaseRepository):
    model = CategoryORM
    mapper = CategoryDataMapper
