# src/middleware/siem.py
from fastapi import Request
from src.siem import log_event, current_correlation_id
from src.main import app
from uuid import uuid
@app.middleware("http")
async def siem_middleware(request: Request, call_next):
    global current_correlation_id
    current_correlation_id = str(uuid.uuid4())
    
    # Лог start запроса
    await log_event(
        "request_start",
        details={
            "method": request.method,
            "path": request.url.path,
            "ip": request.client.host
        }
    )
    
    response = await call_next(request)
    
    # Лог end запроса
    await log_event(
        "request_end",
        details={
            "status_code": response.status_code,
            "correlation_id": current_correlation_id
        }
    )
    return response
