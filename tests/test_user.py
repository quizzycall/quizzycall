from httpx import AsyncClient
import pytest
from validation.registration import RegistrationUser


@pytest.mark.order(1)
@pytest.mark.parametrize('email, nickname, password', [
    ('1@example.com', '1', '1'),
    ('2@example.com', '2', '2'),
    ('3@example.com', '3', '3'),
    ('4@example.com', '4', '4')
])
async def test_registration_user(ac: AsyncClient, email, nickname, password):
    reg_data = RegistrationUser(email=email, nickname=nickname, password=password)
    res = await ac.post('/api/user/registration-user', json=reg_data.dict())
    ac.headers[f'user_{nickname}_token'] = res.json().get('access_token')
    assert res.status_code == 200


@pytest.mark.parametrize('email, nickname, password', [
    ('11@example.com', '1', '1'),  # existing email
    ('2@example.com', '11', '1')  # existing nickname
])
async def test_registration_user_error(ac: AsyncClient, email, nickname, password):
    ac.headers["content-type"] = 'application/json'
    reg_data = RegistrationUser(email=email, nickname=nickname, password=password)
    res = await ac.post('/api/user/registration-user', json=reg_data.dict())
    assert res.status_code == 400


@pytest.mark.order(2)
async def test_login_usr(ac: AsyncClient):
    ac.headers["content-type"] = "application/x-www-form-urlencoded"
    login_data = {
        "username": '1',
        "password": "1",
    }
    res = await ac.post('/api/user/login-user', data=login_data)
    assert res.status_code == 200
    ac.headers["token"] = res.json().get('access_token')


@pytest.mark.parametrize('username, password', [
    ('11', '12121212'),  # wrong pass
    ('111212', '1')  # non-existing user
])
async def test_login_usr_error(ac: AsyncClient, username, password):
    ac.headers["content-type"] = "application/x-www-form-urlencoded"
    login_data = {
        "username": username,
        "password": password,
    }
    res = await ac.post('/api/user/login-user', data=login_data)
    assert res.status_code == 400


@pytest.mark.order(7)
async def test_email_validation(ac: AsyncClient):
    res = await ac.get(f'/api/user/email-validation/{ac.headers["token"]}')
    assert res.status_code == 200
