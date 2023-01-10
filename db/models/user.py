from sqlmodel import SQLModel, Field, BigInteger, Column


class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str
    hashed_password: str
    nickname: str
    is_email_verified: bool = Field(default=False)
    phone: int = Field(default=None)
    is_admin: bool = Field(default=False)
    points: int = Field(default=0, sa_column=Column(BigInteger()))
