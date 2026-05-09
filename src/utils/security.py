from src.init import redis_manager
from src.config import settings
from src.siem import log_event


async def check_blocked(key_prefix: str, ident: str) -> bool:
    key = f"blocked:{key_prefix}:{ident}"
    is_blocked = bool(await redis_manager.get(key))

    if is_blocked:
        await log_event(
            event="security.check_blocked",
            severity="warning",
            details={
                "key_prefix": key_prefix,
                "ident": ident,
                "blocked": True,
            },
        )

    return is_blocked


async def register_failed_attempt(key_prefix: str, ident: str) -> int:
    fail_key = f"failed:{key_prefix}:{ident}"
    block_key = f"blocked:{key_prefix}:{ident}"

    raw = await redis_manager.get(fail_key)
    attempts = int(raw) if raw else 0
    attempts += 1

    await redis_manager.set(
        fail_key,
        str(attempts),
        expire=settings.FAILED_TTL_SECONDS,
    )

    await log_event(
        event="security.failed_attempt",
        severity="info",
        details={
            "key_prefix": key_prefix,
            "ident": ident,
            "attempts": attempts,
        },
    )

    if attempts >= settings.ATTEMPT_LIMIT:
        await redis_manager.set(
            block_key,
            "1",
            expire=settings.BLOCK_TIME_SECONDS,
        )

        await log_event(
            event="security.blocked",
            severity="warning",
            details={
                "key_prefix": key_prefix,
                "ident": ident,
                "attempts": attempts,
                "limit": settings.ATTEMPT_LIMIT,
            },
        )

    elif attempts == settings.ATTEMPT_LIMIT - 1:
        await log_event(
            event="security.warning_threshold",
            severity="warning",
            details={
                "key_prefix": key_prefix,
                "ident": ident,
                "attempts": attempts,
            },
        )

    return attempts


async def reset_attempts(key_prefix: str, ident: str) -> None:
    await redis_manager.delete(f"failed:{key_prefix}:{ident}")

    await log_event(
        event="security.reset_attempts",
        severity="info",
        details={
            "key_prefix": key_prefix,
            "ident": ident,
        },
    )