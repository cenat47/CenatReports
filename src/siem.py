# src/siem.py
import httpx
import uuid
from datetime import datetime
from contextvars import ContextVar
from config import settings

correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def set_correlation_id():
    cid = str(uuid.uuid4())
    correlation_id_ctx.set(cid)
    return cid


def get_correlation_id():
    return correlation_id_ctx.get()


async def log_event(
    event: str,
    user_id: uuid.UUID | None = None,
    details: dict | None = None,
    severity: str = "info",
):
    doc = {
        "@timestamp": datetime.utcnow().isoformat(),
        "correlation_id": get_correlation_id(),
        "event": event,
        "severity": severity,
        "user_id": str(user_id) if user_id else None,
        "service": "cenatreports-api",
        **(details or {}),
    }

    async with httpx.AsyncClient() as client:
        await client.post(settings.ELASTICSEARCH_URL, json=doc)
