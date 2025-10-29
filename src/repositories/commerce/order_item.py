from src.repositories.mapper.mappers import OrderItemDataMapper
from src.models.commerce.order_item import OrderItemOrm
from src.repositories.base import BaseRepository


class OrderItemRepository(BaseRepository):
    model = OrderItemOrm
    mapper = OrderItemDataMapper