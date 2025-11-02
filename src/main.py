import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI

sys.path.append(str(Path(__file__).parent.parent))

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from src.init import redis_manager
from src.api.auth import router as auth_router 

@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    logging.info("FastAPI cache initialized")
    yield
    await redis_manager.close()


logging.basicConfig(level=logging.DEBUG)

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
