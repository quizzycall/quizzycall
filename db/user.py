from fastapi import HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlmodel import select
from db.models.user import Users
from validation.registration import RegistrationUser
from security.password import PasswordHash
from security.jwt import create_token, verify_token
from sqlalchemy.ext.asyncio import AsyncSession


async def create_user(user: RegistrationUser, session: AsyncSession):
    user = dict(user)
    _r_e = await session.execute(select(Users).where(Users.email == user['email']))
    if _r_e.scalar_one_or_none():
        raise HTTPException(status_code=400, detail='Email is already registered')
    _r_n = await session.execute(select(Users).where(Users.nickname == user['nickname']))
    if _r_n.scalar_one_or_none():
        raise HTTPException(status_code=400, detail='Nickname is already registered')
    hashed_password = PasswordHash().get_password_hash(user["password"])
    user_db = Users(email=user["email"], hashed_password=hashed_password, nickname=user["nickname"])
    if user.get('phone'):
        user_db.phone = user['phone']
    session.add(user_db)
    await session.commit()

    return create_token({'login': user["nickname"]})


async def login_user(user: OAuth2PasswordRequestForm, session: AsyncSession):
    user = {'login': user.username, 'password': user.password}
    r = await session.execute(select(Users).where(Users.email == user["login"] or Users.nickname == user["login"]))
    result = r.scalar_one_or_none()
    if result:
        if PasswordHash().verify_password(user["password"], result.hashed_password):
            return create_token({'login': user["login"]})
        else:
            raise HTTPException(status_code=400, detail="Wrong password!")
    else:
        raise HTTPException(status_code=400, detail="User non-exists")


async def validate_email_token(token: str, session: AsyncSession):
    login = verify_token(token)
    r = await session.execute(select(Users).where(Users.email == login or Users.nickname == login))
    result = r.scalar_one_or_none()
    result.is_email_verified = True
    await session.commit()
    print(45787845784578388338)
    return True


async def get_user_data(login: str, session: AsyncSession):
    r = await session.execute(select(Users).where(Users.email == login or Users.nickname == login))
    return r.scalar_one_or_none()
