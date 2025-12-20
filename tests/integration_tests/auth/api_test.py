import pytest
from tests.conftest import register_data


@pytest.mark.asyncio
async def test_login_success(ac):
    resp = await ac.post("/auth/login", json=register_data)
    assert resp.status_code == 200
    assert "access_token" and "refresh_token" in ac.cookies


@pytest.mark.asyncio
async def test_login_wrong_password(ac):
    ac.cookies.clear()
    resp = await ac.post(
        "/auth/login",
        json={"email": register_data["email"], "password": "Wrong1234"},
    )
    assert resp.status_code == 401
    assert "access_token" not in ac.cookies


@pytest.mark.asyncio
async def test_admin_status_requires_auth(ac):
    resp = await ac.get("/admin/status")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_manager_exists_in_db(db):
    result = await db.user.get_one(role="manager")
    assert result is not None
    assert result.role == "manager"

@pytest.mark.asyncio
async def test_refresh_token_success(ac):
    resp = await ac.post("/auth/login", json=register_data)
    assert resp.status_code == 200
    refresh_token = ac.cookies.get("refresh_token")
    assert refresh_token is not None

    ac.cookies.clear()
    ac.cookies.set("refresh_token", refresh_token)

    refresh_resp = await ac.post("/auth/refresh")
    assert refresh_resp.status_code == 200
    assert "access_token" in ac.cookies

@pytest.mark.asyncio
async def test_refresh_token_invalid(ac):
    ac.cookies.clear()
    ac.cookies.set("refresh_token", "invalid_token")

    refresh_resp = await ac.post("/auth/refresh")
    assert refresh_resp.status_code == 401
    assert "access_token" not in ac.cookies

@pytest.mark.asyncio
async def test_logout(ac):
    ac.cookies.clear()
    resp = await ac.post("/auth/login", json=register_data)
    assert resp.status_code == 200
    assert "access_token" in ac.cookies
    assert "refresh_token" in ac.cookies

    logout_resp = await ac.post("/auth/logout")
    assert logout_resp.status_code == 200
    assert "access_token" not in ac.cookies
    assert "refresh_token" not in ac.cookies
