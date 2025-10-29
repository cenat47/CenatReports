from src.repositories.mapper.mappers import OrderDataMapper
from src.models.commerce.order import OrderORM
from src.repositories.base import BaseRepository


class OrderRepository(BaseRepository):
    model = OrderORM
    mapper = OrderDataMapper