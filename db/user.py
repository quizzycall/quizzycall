from fastapi import HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Session, create_engine, select
from db.models.user import Users
from validation.registration import RegistrationUser
from security.password import PasswordHash
from security.jwt import create_token, verify_token
from security.config import Config as cfg

engine = create_engine(cfg.PSQL_URL, pool_pre_ping=True)

SQLModel.metadata.create_all(engine)

session = Session(engine)


def create_user(user: RegistrationUser):
    user = dict(user)
    hashed_password = PasswordHash().get_password_hash(user["password"])
    user_db = Users(email=user["email"], hashed_password=hashed_password, nickname=user["nickname"])
    session.add(user_db)
    session.commit()
    return create_token({'login': user["nickname"]})


def login_user(user: OAuth2PasswordRequestForm):
    user = {'login': user.username, 'password': user.password}
    result = session.exec(select(Users).where(Users.email == user["login"] or Users.nickname == user["login"])).first()
    if result:
        if PasswordHash().verify_password(user["password"], result.hashed_password):
            return create_token({'login': user["login"]})
        else:
            raise HTTPException(status_code=400, detail="Wrong password!")
    else:
        raise HTTPException(status_code=400, detail="User non-exists")


def validate_email_token(token: str):
    login = verify_token(token)
    result = session.exec(select(Users).where(Users.email == login or Users.nickname == login)).first()
    result.is_email_verified = True
    session.commit()
    return True


def get_user_data(login: str):
    return session.exec(select(Users).where(Users.email == login or Users.nickname == login)).first()