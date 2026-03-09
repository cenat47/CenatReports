# src/middleware/siem.py
from fastapi import Request
from src.siem import log_event, set_correlation_id
from src.main import app
import time


@app.middleware("http")
async def siem_middleware(request: Request, call_next):
    correlation_id = set_correlation_id()
    start_time = time.time()

    await log_event(
        "http_request_start",
        details={
            "http.method": request.method,
            "http.path": request.url.path,
            "client.ip": request.client.host,
        },
    )

    response = await call_next(request)

    duration = int((time.time() - start_time) * 1000)

    await log_event(
        "http_request_end",
        details={
            "http.status_code": response.status_code,
            "duration_ms": duration,
        },
        severity="error" if response.status_code >= 500 else "info",
    )

    response.headers["X-Correlation-ID"] = correlation_id
    return response
