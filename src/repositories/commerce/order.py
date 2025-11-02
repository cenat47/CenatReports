from src.models.commerce.order import OrderORM
from src.repositories.base import BaseRepository
from src.repositories.mapper.mappers import OrderDataMapper


class OrderRepository(BaseRepository):
    model = OrderORM
    mapper = OrderDataMapper
