from src.models.commerce.customer import CustomerORM
from src.repositories.base import BaseRepository
from src.repositories.mapper.mappers import CustomerDataMapper


class CustomerRepository(BaseRepository):
    model = CustomerORM
    mapper = CustomerDataMapper
