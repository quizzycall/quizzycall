from httpx import AsyncClient
from fastapi import HTTPException
from security.jwt import create_token
from db.edit_user import change_password_with_email
from db.user import get_user_data
from sqlalchemy.ext.asyncio import AsyncSession
from security.password import PasswordHash
import pytest


@pytest.mark.order(3)
async def test_change_pass_with_old_pass(ac: AsyncClient, session: AsyncSession):
    ac.headers['Authorization'] = f"Bearer {ac.headers.get('token')}"
    res = await ac.patch("/api/edit-user/change-password-with-old-password/11/1")
    assert res.status_code == 200
    user = await get_user_data('1', session)
    assert PasswordHash.verify_password('11', user.hashed_password) is True


@pytest.mark.order(4)
async def test_change_nick(ac: AsyncClient, session: AsyncSession):
    res = await ac.patch("/api/edit-user/change-nickname/11")
    assert res.status_code == 200
    user = await get_user_data('11', session)
    assert user.nickname == '11'
    ac.headers["content-type"] = "application/x-www-form-urlencoded"
    login_data = {
        "username": '11',
        "password": "11",
    }
    res = await ac.post('/api/user/login-user', data=login_data)
    assert res.status_code == 200
    ac.headers["token"] = res.json().get('access_token')
    ac.headers['Authorization'] = f"Bearer {ac.headers.get('token')}"
    ac.headers["login"] = '11'


@pytest.mark.order(5)
async def test_change_phone_num(ac: AsyncClient, session: AsyncSession):
    res = await ac.patch("/api/edit-user/change-phone-number/3737812")
    assert res.status_code == 200
    user = await get_user_data('11', session)
    assert user.phone == '3737812'


@pytest.mark.order(6)
async def test_change_pass_with_email_error(ac: AsyncClient, session: AsyncSession):
    try:
        await change_password_with_email('12', ac.headers.get('login'), session)
    except HTTPException as e:
        assert e.status_code == 400


async def test_change_pass_with_email(ac: AsyncClient, session: AsyncSession):
    r = await change_password_with_email('12', ac.headers.get('login'), session)
    res = await ac.get(f"/api/edit-user/change-password-with-email-validation/{r['token']}")
    assert res.status_code == 200
    user = await get_user_data('11', session)
    assert PasswordHash.verify_password('12', user.hashed_password) is True


async def test_change_user_email(ac: AsyncClient, session: AsyncSession):
    res = await ac.get(f"/api/edit-user/change-email-validation/"
                       f"{create_token({'new_email': '11@example.com', 'login': ac.headers.get('login')})}")
    assert res.status_code == 200
    user = await get_user_data('11', session)
    assert user.email == '11@example.com'

