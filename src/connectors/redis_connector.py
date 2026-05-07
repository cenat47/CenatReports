import logging

import redis.asyncio as redis
from redis.exceptions import ConnectionError

from src.siem import log_event


class RedisManager:
    def __init__(self, host: str, port: int, password: str | None = None):
        self.host = host
        self.port = port
        self.password = password
        self.redis: redis.Redis | None = None

    async def connect(self) -> bool:
        logging.info(f"Начало подключения к Redis host={self.host}, port={self.port}")

        await log_event(
            "redis_connect_attempt",
            details={
                "redis.host": self.host,
                "redis.port": self.port,
            },
        )

        try:
            self.redis = await redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
            )
            await self.redis.ping()

            logging.info(
                f"Успешное подключение к Redis host={self.host}, port={self.port}"
            )

            await log_event(
                "redis_connect_success",
                details={
                    "redis.host": self.host,
                    "redis.port": self.port,
                },
            )

            return True

        except ConnectionError as e:
            logging.error(
                f"Не удалось подключиться к Redis {self.host}:{self.port}: {e}"
            )

            await log_event(
                "redis_connect_failed",
                details={
                    "redis.host": self.host,
                    "redis.port": self.port,
                    "error": str(e),
                },
                severity="error",
            )

            return False

        except Exception as e:
            logging.error(f"Неожиданная ошибка при подключении к Redis: {e}")

            await log_event(
                "redis_connect_exception",
                details={
                    "redis.host": self.host,
                    "redis.port": self.port,
                    "error": str(e),
                },
                severity="critical",
            )
            return False
    async def set(self, key: str, value: str, expire: int | None = None):
        if not self.redis:
            raise ConnectionError("Redis не подключён")
        await self.redis.set(key, value, ex=expire) if expire else await self.redis.set(
            key, value
        )
        await log_event(
            "redis_set",
            details={
                "redis.key": key,
                "expire": expire,
            },
        )

    async def get(self, key: str) -> str | None:
        if not self.redis:
            raise ConnectionError("Redis не подключён")
        result = await self.redis.get(key)
        if result is not None:
            return result.decode()
        return None

    async def delete(self, key: str):
        if not self.redis:
            raise ConnectionError("Redis не подключён")
        await self.redis.delete(key)



    async def close(self):
        if self.redis:
            await self.redis.close()

            await log_event(
                "redis_connection_closed",
                details={
                    "redis.host": self.host,
                    "redis.port": self.port,
                },
            )

            self.redis = None