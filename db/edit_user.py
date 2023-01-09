from fastapi import HTTPException, BackgroundTasks
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlmodel import select
from db.models.user import Users
from validation.registration import RegistrationUser
from security.password import PasswordHash
from security.jwt import create_token, decode_token
from .user import get_user_data
from .settings import session
from security.email import send_change_password_email, send_email_changing


def change_password_with_old_password(new_pass: str, old_pass: str, login: str):
    user = get_user_data(login)
    if not PasswordHash.verify_password(old_pass, user.hashed_password):
        raise HTTPException(status_code=400, detail='Wrong old password')
    user.hashed_password = PasswordHash.get_password_hash(new_pass)
    session.commit()
    return {'msg': 'Password changed'}


async def send_change_password_with_email(new_pass: str, url: str, login: str, back_tasks: BackgroundTasks):
    user = get_user_data(login)
    if not user.is_email_verified:
        raise HTTPException(status_code=400, detail='Email is not verified')
    token = create_token({'login': login, 'new_pass': new_pass})
    await send_change_password_email(user.email, url + f'?token={token}', back_tasks)
    return {'msg': 'Password change email was sent'}


def change_password_after_email(token: str):
    decoded_token = decode_token(token)
    try:
        user = get_user_data(decoded_token['login'])
        user.hashed_password = PasswordHash.get_password_hash(decoded_token['new_pass'])
        session.commit()
        return {'msg': 'Password changed'}
    except:
        raise HTTPException(status_code=400, detail='Invalid token')


async def change_email(new_email: EmailStr, url: str, login: str, back_tasks: BackgroundTasks):
    token = create_token({'new_email': new_email, 'login': login})
    url += f'?token={token}'
    await send_email_changing(new_email, url, back_tasks)
    return {'msg': 'Email changing was sent'}


def change_email_validation(token: str):
    decoded_token = decode_token(token)
    try:
        user = get_user_data(decoded_token['login'])
        user.email = decoded_token['new_email']
        session.commit()
        return {'msg': 'Email was changed'}
    except:
        raise HTTPException(status_code=400, detail='Invalid token')


def change_nickname(new_nick: str, login: str):
    user = get_user_data(login)
    user.nickname = new_nick
    session.commit()
    return {'msg': 'Nickname was changed'}


def change_phone(new_phone: int, login: str):
    user = get_user_data(login)
    user.phone = new_phone
    session.commit()
    return {'msg': 'Phone was changed'}
