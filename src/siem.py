import uuid
from datetime import datetime, timezone
from contextvars import ContextVar

import httpx
from fastapi.encoders import jsonable_encoder

from src.config import settings


correlation_id_ctx: ContextVar[str | None] = ContextVar(
    "correlation_id",
    default=None,
)

status_code_ctx: ContextVar[int | None] = ContextVar(
    "status_code",
    default=None,
)


def set_correlation_id() -> str:
    cid = str(uuid.uuid4())
    correlation_id_ctx.set(cid)
    return cid


def get_correlation_id() -> str | None:
    return correlation_id_ctx.get()


def set_status_code(status_code: int) -> None:
    status_code_ctx.set(status_code)


def get_status_code() -> int | None:
    return status_code_ctx.get()


async def log_event(
    event: str,
    user_id: uuid.UUID | None = None,
    details: dict | None = None,
    severity: str = "info",
) -> None:
    """
    Отправка события в Elasticsearch
    """

    doc = {
        "@timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "severity": severity,
        "service": "cenatreports-api",
        "correlation_id": get_correlation_id(),
    }

    status_code = get_status_code()
    if status_code is not None:
        doc["http.status_code"] = status_code

    if user_id is not None:
        doc["user_id"] = str(user_id)

    if details:
        doc.update(details)

    doc = jsonable_encoder(doc)

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.post(
                settings.ELASTICSEARCH_URL,
                json=doc,
            )
            response.raise_for_status()

    except Exception as e:
        print(f"[SIEM ERROR] {e}")
        print(f"[SIEM DOC] {doc}")