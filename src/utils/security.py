from src.init import redis_manager
from src.config import settings


async def check_blocked(key_prefix: str, ident: str) -> bool:
    key = f"blocked:{key_prefix}:{ident}"
    return bool(await redis_manager.get(key))


async def register_failed_attempt(key_prefix: str, ident: str) -> int:
    fail_key = f"failed:{key_prefix}:{ident}"
    block_key = f"blocked:{key_prefix}:{ident}"
    raw = await redis_manager.get(fail_key)
    attempts = int(raw) if raw else 0
    attempts += 1
    await redis_manager.set(fail_key, str(attempts), expire=settings.FAILED_TTL_SECONDS)
    if attempts >= settings.ATTEMPT_LIMIT:
        await redis_manager.set(block_key, "1", expire=settings.BLOCK_TIME_SECONDS)
    return attempts


async def reset_attempts(key_prefix: str, ident: str) -> None:
    await redis_manager.delete(f"failed:{key_prefix}:{ident}")
