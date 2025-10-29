from src.repositories.mapper.mappers import CategoryDataMapper
from src.models.commerce.category import CategoryORM
from src.repositories.base import BaseRepository


class CategoryRepository(BaseRepository):
    model = CategoryORM
    mapper = CategoryDataMapper