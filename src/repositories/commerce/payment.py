from src.repositories.mapper.mappers import PaymentDataMapper
from src.models.commerce.payment import PaymentORM
from src.repositories.base import BaseRepository


class PaymentRepository(BaseRepository):
    model = PaymentORM
    mapper = PaymentDataMapper