# schemas/audit.py
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional
import uuid


# === Типы действий (СНАЧАЛА определяем Enum) ===
class AuditAction(str, Enum):
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGOUT = "LOGOUT"
    ABORT_ALL_SESSIONS = "ABORT_ALL_SESSIONS"
    TOKEN_REFRESH = "TOKEN_REFRESH"
    ROLE_CHANGE_REQUEST = "ROLE_CHANGE_REQUEST"
    ROLE_CHANGE_CONFIRM = "ROLE_CHANGE_CONFIRM"
    REPORT_GENERATE = "REPORT_GENERATE"
    REPORT_DOWNLOAD = "REPORT_DOWNLOAD"
    ACCESS_DENIED = "ACCESS_DENIED"


# === Схема для создания записи аудита ===
class AuditLogCreate(BaseModel):
    user_id: Optional[uuid.UUID] = None
    action: AuditAction
    table_name: Optional[str] = None
    record_id: Optional[str] = None
    old_values: Optional[dict[str, Any]] = None
    new_values: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[str] = None


class Audit(AuditLogCreate):
    id: int


# === Схема для ответа API ===
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[uuid.UUID]
    action: AuditAction
    table_name: Optional[str]
    record_id: Optional[str]
    old_values: Optional[dict[str, Any]]
    new_values: Optional[dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    details: Optional[str]
    created_at: datetime


# === Параметры фильтрации для просмотра аудит-логов ===
class AuditLogParams(BaseModel):
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    user_id: Optional[uuid.UUID] = None
    action: Optional[AuditAction] = None
    table_name: Optional[str] = None
    limit: int = 100
    offset: int = 0
