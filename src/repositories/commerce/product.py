from src.repositories.mapper.mappers import ProductDataMapper
from src.models.commerce.product import ProductORM
from src.repositories.base import BaseRepository


class ProductRepository(BaseRepository):
    model = ProductORM
    mapper = ProductDataMapper