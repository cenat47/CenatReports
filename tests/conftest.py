from datetime import datetime, timezone
from unittest import mock

import pytest
from httpx import ASGITransport, AsyncClient

from src.models.report.report_template import ReportTemplateORM
from src.models.auth.user import UserORM
from src.api.dependencies import get_db
from src.config import settings
from src.database import Base, async_session_maker_null_pооl, engine_null_pool
from src.main import app
from src.models import *  # noqa: F403
from utils.db_manager import DBManager


from src.services import auth as auth_service_module
from src.connectors import redis_connector
from utils.password_utils import get_password_hash


class DummyRedis:
    async def set(self, *args, **kwargs):
        return True

    async def get(self, *args, **kwargs):
        return None

    async def delete(self, *args, **kwargs):
        return True


@pytest.fixture(scope="session", autouse=True)
def patch_redis():
    dummy = DummyRedis()
    if hasattr(auth_service_module, "redis_manager"):
        auth_service_module.redis_manager.redis = dummy
    with mock.patch.object(redis_connector.RedisManager, "connect", return_value=None):
        yield


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


async def get_db_null_pool():
    async with DBManager(session_factory=async_session_maker_null_pооl) as db:
        yield db


@pytest.fixture()
async def db() -> DBManager:  # type: ignore
    async for db in get_db_null_pool():
        yield db


app.dependency_overrides[get_db] = get_db_null_pool


@pytest.fixture(scope="session", autouse=True)
async def setup_db(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker_null_pооl() as session:
        password_hash = get_password_hash("Manager1234")
        stmt = UserORM(
            email="manager@lol.lol",
            password_hash=password_hash,
            first_name="Test",
            last_name="Manager",
            role="manager",
            is_active=True,
            is_verified=True,
            registered_at=datetime.now(timezone.utc),
        )
        session.add(stmt)
        await session.commit()
    async with async_session_maker_null_pооl() as session:
        template = ReportTemplateORM(
            name="daily_sales",
            description="",
            allowed_roles="manager",
        )
        session.add(template)
        await session.commit()


@pytest.fixture(scope="session", autouse=True)
async def ac():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


register_data = {"email": "test@fe.fd", "password": "Pass1234"}
register_manager = {"email": "manager@lol.lol", "password": "Manager1234"}


@pytest.fixture(scope="session", autouse=True)
async def register_user(setup_db, ac):
    await ac.post(url="/auth/register", json=register_data)


@pytest.fixture(scope="session")
async def authenticated_ac(register_user, ac):
    await ac.post(url="/auth/login", json=register_data)
    assert ac.cookies["access_token"]
    yield ac


@pytest.fixture(scope="session")
async def authenticated_manager(register_user, ac):
    await ac.post(url="/auth/login", json=register_manager)
    assert ac.cookies["access_token"]
    yield ac
