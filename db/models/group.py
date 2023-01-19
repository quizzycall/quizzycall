from sqlmodel import Column, Field, SQLModel, BigInteger


class Group(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    creator_id: int = Field(default=None, foreign_key="users.id")
    description: str
    points: int = Field(default=0, sa_column=Column(BigInteger()))