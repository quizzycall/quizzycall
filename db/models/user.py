from sqlmodel import SQLModel, Field

class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    mail: str
    hashed_password: str
    username: str