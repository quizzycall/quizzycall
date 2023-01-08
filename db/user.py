from fastapi import HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Session, create_engine, select
from db.models.user import Users
from validation.login import LoginUser
from validation.registration import RegistrationUser
from security.password import PasswordHash
from security.jwt import create_token
import os

engine = create_engine(os.getenv("PSQL_URL"))

SQLModel.metadata.create_all(engine)

session = Session(engine)

def CreateUser(user: RegistrationUser):
    user = dict(user)
    hashed_password = PasswordHash().get_password_hash(user["password"])
    #user_db = Users(email=user["email"], hashed_password=hashed_password, username=user["nickname"])
    user_db = Users(email=user["email"], hashed_password=hashed_password, nickname=user["nickname"])
    session.add(user_db)
    session.commit()
    return create_token({'login': user["nickname"]})

def LoginUser(user: OAuth2PasswordRequestForm):
    user = {'login': user.username, 'password': user.password}
    result = session.exec(select(Users).where(Users.email==user["login"] or Users.nickname==user["login"])).first()
    if result:
        if PasswordHash().verify_password(user["password"], result.hashed_password):
            return create_token({'login': user["login"]})
        else:
            raise HTTPException(status_code=400, detail="Wrong password!")
    else:
        raise HTTPException(status_code=400, detail="User non-exists")
