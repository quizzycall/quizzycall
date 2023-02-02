from sqlmodel import SQLModel, Field, BigInteger, Column, Integer
from sqlalchemy.dialects import postgresql
from typing import List


class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str
    hashed_password: str
    nickname: str
    is_email_verified: bool = Field(default=False)
    phone: str = Field(default=None)
    is_admin: bool = Field(default=False)
    points: int = Field(default=0, sa_column=Column(BigInteger()))
    groups_id: List[int] = Field(default=[], sa_column=Column(postgresql.ARRAY(Integer())))
