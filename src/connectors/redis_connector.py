import logging

import redis.asyncio as redis
from redis.exceptions import ConnectionError


class RedisManager:
    def __init__(self, host: str, port: int, password: str | None = None):
        self.host = host
        self.port = port
        self.password = password
        self.redis: redis.Redis | None = None

    async def connect(self) -> bool:
        logging.info(f"Начало подключения к Redis host={self.host}, port={self.port}")
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
            return True
        except ConnectionError as e:
            logging.error(
                f"Не удалось подключиться к Redis {self.host}:{self.port}: {e}"
            )
            return False
        except Exception as e:
            logging.error(f"Неожиданная ошибка при подключении к Redis: {e}")
            return False

    async def set(self, key: str, value: str, expire: int | None = None):
        if not self.redis:
            raise ConnectionError("Redis не подключён")
        if expire:
            await self.redis.set(key, value, ex=expire)
        else:
            await self.redis.set(key, value)

    async def get(self, key: str) -> str | None:
        if not self.redis:
            raise ConnectionError("Redis не подключён")
        result = await self.redis.get(key)
        if result is not None:
            return result.decode()  # чтобы возвращать str вместо bytes
        return None

    async def delete(self, key: str):
        if not self.redis:
            raise ConnectionError("Redis не подключён")
        await self.redis.delete(key)

    async def close(self):
        if self.redis:
            await self.redis.close()
            self.redis = None
