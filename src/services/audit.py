from schemas.security.audit import AuditLogCreate
from services.base import BaseService


class AuditService(BaseService):
    async def log(self, data: AuditLogCreate):
        await self.db.audit.add(data)
        await self.db.commit()
