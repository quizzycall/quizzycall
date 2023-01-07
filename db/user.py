from sqlmodel import SQLModel, Session, create_engine, select
from db.models.user import Users
from validation.login import LoginUser
from validation.registration import RegistrationUser
from security.password import PasswordHash
import os

engine = create_engine(os.getenv("PSQL_URL"))

SQLModel.metadata.create_all(engine)

session = Session(engine)

def CreateUser(user: RegistrationUser):
    user = dict(user)
    hashed_password = PasswordHash().get_password_hash(user["password"])
    user_db = Users(email=user["email"], hashed_password=hashed_password, username=user["nickname"])
    session.add(user_db)
    session.commit()
    return dict(user_db)

def LoginUser(user: LoginUser):
    user = dict(user)
    result = session.exec(select(Users).where(Users.email==user["login"])).first()
    if result:
        if PasswordHash().verify_password(user["password"], result.hashed_password):
            return f"Hello, {result.nickname}"
        else:
            return "Wrong password!"
    else:
        return "User non-exists"