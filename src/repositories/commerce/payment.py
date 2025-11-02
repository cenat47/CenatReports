from src.models.commerce.payment import PaymentORM
from src.repositories.base import BaseRepository
from src.repositories.mapper.mappers import PaymentDataMapper


class PaymentRepository(BaseRepository):
    model = PaymentORM
    mapper = PaymentDataMapper
