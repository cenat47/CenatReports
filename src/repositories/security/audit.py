from src.models.security.audit import AuditORM
from src.repositories.mapper.mappers import AuditDataMapper
from src.repositories.base import BaseRepository


class AuditRepository(BaseRepository):
    model = AuditORM
    mapper = AuditDataMapper
