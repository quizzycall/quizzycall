from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from security.password import PasswordHash
from security.jwt import create_token, decode_token
from .user import get_user_data, get_user_by_email


async def change_password_with_old_password(new_pass: str, old_pass: str, login: str, session: AsyncSession):
    user = await get_user_data(login, session)
    if not PasswordHash.verify_password(old_pass, user.hashed_password):
        raise HTTPException(status_code=400, detail='Wrong old password')
    user.hashed_password = PasswordHash.get_password_hash(new_pass)
    await session.commit()
    return {'msg': 'Password changed'}


async def change_password_with_email(new_pass: str, login: str, session: AsyncSession):
    user = await get_user_data(login, session)
    token = create_token({'login': login, 'new_pass': new_pass})
    return {'status': 200, 'token': token, 'email': user.email}


async def change_password_after_email(token: str, session: AsyncSession):
    decoded_token = decode_token(token)
    try:
        user = await get_user_data(decoded_token['login'], session)
        user.hashed_password = PasswordHash.get_password_hash(decoded_token['new_pass'])
        await session.commit()
        return {'msg': 'Password changed'}
    except:
        raise HTTPException(status_code=400, detail='Invalid token')


async def change_email(new_email: EmailStr, login: str, session: AsyncSession):
    token = create_token({'new_email': new_email, 'login': login})
    user = await get_user_data(login, session)
    if user.is_email_verified:
        user.is_email_verified = False
        await session.commit()
    if await get_user_by_email(new_email, session):
        raise HTTPException(status_code=400, detail='There is already an account with such email')
    return {'status': 200, 'token': token}


async def change_email_validation(token: str, session: AsyncSession):
    decoded_token = decode_token(token)
    try:
        user = await get_user_data(decoded_token['login'], session)
        user.email = decoded_token['new_email']
        user.is_email_verified = True
        await session.commit()
        return {'msg': 'Email was changed'}
    except:
        raise HTTPException(status_code=400, detail='Invalid token')


async def change_nickname(new_nick: str, login: str, session: AsyncSession):
    user = await get_user_data(login, session)
    user.nickname = new_nick
    await session.commit()
    return {'msg': 'Nickname was changed'}


async def change_phone(new_phone: str, login: str, session: AsyncSession):
    user = await get_user_data(login, session)
    user.phone = new_phone
    await session.commit()
    return {'msg': 'Phone was changed'}
