from src.repositories.mapper.mappers import CustomerDataMapper
from src.models.commerce.customer import CustomerORM
from src.repositories.base import BaseRepository


class CustomerRepository(BaseRepository):
    model = CustomerORM
    mapper = CustomerDataMapper