from src.repositories.mapper.mappers import SupplierDataMapper
from src.models.commerce.supplier import SupplierORM
from src.repositories.base import BaseRepository


class SupplierRepository(BaseRepository):
    model = SupplierORM
    mapper = SupplierDataMapper