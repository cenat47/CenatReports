# src/siem.py
import httpx
import uuid
from datetime import datetime
from config import settings

async def log_event(event: str, user_id: uuid.UUID | None = None, details: dict = None):
    """Отправляет событие в Elasticsearch"""
    doc = {
        "@timestamp": datetime.utcnow().isoformat(),
        "correlation_id": str(uuid.uuid4()),          
        "event": event,
        "user_id": str(user_id) if user_id else None, 
        "app": "CenatReports",
        **{k: str(v) if isinstance(v, (uuid.UUID, datetime)) else v for k, v in (details or {}).items()}
    }
    async with httpx.AsyncClient() as client:
        await client.post(settings.ELASTICSEARCH_URL, json=doc)

current_correlation_id = None
