from sqlmodel import SQLModel, Field


class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str
    hashed_password: str
    nickname: str
    is_email_verified: bool = Field(default=False)
