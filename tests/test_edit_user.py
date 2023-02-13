from httpx import AsyncClient
from fastapi import HTTPException
from security.jwt import create_token
from db.edit_user import change_password_with_email, change_email
from sqlalchemy.ext.asyncio import AsyncSession
from conftest import domain
import pytest


@pytest.mark.order(3)
async def test_change_pass_with_old_pass(ac: AsyncClient):
    ac.headers['Authorization'] = f"Bearer {ac.headers.get('token')}"
    res = await ac.patch("/api/edit-user/change-password-with-old-password/11/1")
    assert res.status_code == 200


@pytest.mark.order(4)
async def test_change_nick(ac: AsyncClient):
    res = await ac.patch("/api/edit-user/change-nickname/11")
    assert res.status_code == 200
    ac.headers["content-type"] = "application/x-www-form-urlencoded"
    login_data = {
        "username": '11',
        "password": "11",
    }
    res = await ac.post('/api/user/login_user', data=login_data)
    assert res.status_code == 200
    ac.headers["token"] = res.json().get('access_token')
    ac.headers['Authorization'] = f"Bearer {ac.headers.get('token')}"
    ac.headers["login"] = '11'


@pytest.mark.order(5)
async def test_change_phone_num(ac: AsyncClient):
    res = await ac.patch("/api/edit-user/change-phone-number/3737812")
    assert res.status_code == 200


@pytest.mark.order(6)
async def test_change_pass_with_not_verified_email(ac: AsyncClient, session: AsyncSession):
    try:
        await change_password_with_email('12', ac.headers.get('login'), session)
    except HTTPException as e:
        assert e.status_code == 400


async def test_change_pass_with_email(ac: AsyncClient, session: AsyncSession):
    r = await change_password_with_email('12', ac.headers.get('login'), session)
    res = await ac.get(f"/api/edit-user/change-password-with-email-validation/{r['token']}")
    assert res.status_code == 200


async def test_change_user_email(ac: AsyncClient):
    res = await ac.get(f"/api/edit-user/change-email-validation/"
                       f"{create_token({'new_email': '11@example.com', 'login': ac.headers.get('login')})}")
    assert res.status_code == 200

