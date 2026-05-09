import time

from fastapi import Request

from src.siem import (
    log_event,
    set_correlation_id,
    set_status_code,
)


async def siem_middleware(request: Request, call_next):
    correlation_id = set_correlation_id()
    start_time = time.time()

    client_ip = None
    if request.client:
        client_ip = request.client.host

    await log_event(
        event="http_request_start",
        details={
            "http.method": request.method,
            "http.path": request.url.path,
            "client.ip": client_ip,
            "http.user_agent": request.headers.get("user-agent"),
        },
        severity="info",
    )

    try:
        response = await call_next(request)

    except Exception as e:
        set_status_code(500)

        duration = int((time.time() - start_time) * 1000)

        await log_event(
            event="http_request_error",
            details={
                "http.method": request.method,
                "http.path": request.url.path,
                "client.ip": client_ip,
                "duration_ms": duration,
                "error": str(e),
            },
            severity="error",
        )

        raise

    set_status_code(response.status_code)

    duration = int((time.time() - start_time) * 1000)

    await log_event(
        event="http_request_end",
        details={
            "http.method": request.method,
            "http.path": request.url.path,
            "client.ip": client_ip,
            "duration_ms": duration,
            "http.user_agent": request.headers.get("user-agent"),
        },
        severity = (
            "error"
            if response.status_code >= 500
            else "warning"
            if response.status_code in (401, 403, 404)
            else "info"
        )
            )

    response.headers["X-Correlation-ID"] = correlation_id

    return response