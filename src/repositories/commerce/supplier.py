from src.models.commerce.supplier import SupplierORM
from src.repositories.base import BaseRepository
from src.repositories.mapper.mappers import SupplierDataMapper


class SupplierRepository(BaseRepository):
    model = SupplierORM
    mapper = SupplierDataMapper
