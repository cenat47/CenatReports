from src.models.commerce.product import ProductORM
from src.repositories.base import BaseRepository
from src.repositories.mapper.mappers import ProductDataMapper


class ProductRepository(BaseRepository):
    model = ProductORM
    mapper = ProductDataMapper
