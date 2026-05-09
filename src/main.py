import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

sys.path.append(str(Path(__file__).parent.parent))

from src.api.auth import router as auth_router
from src.api.report import router as report_router
from src.api.admin import router as admin_router
from src.init import redis_manager

from src.middleware.siem import siem_middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()

    FastAPICache.init(
        RedisBackend(redis_manager.redis),
        prefix="fastapi-cache",
    )

    logging.info("FastAPI cache initialized")

    yield

    await redis_manager.close()


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

app = FastAPI(lifespan=lifespan)

app.middleware("http")(siem_middleware)

app.include_router(auth_router)
app.include_router(report_router)
app.include_router(admin_router)


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )