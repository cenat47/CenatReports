from src.models.commerce.order_item import OrderItemOrm
from src.repositories.base import BaseRepository
from src.repositories.mapper.mappers import OrderItemDataMapper


class OrderItemRepository(BaseRepository):
    model = OrderItemOrm
    mapper = OrderItemDataMapper
