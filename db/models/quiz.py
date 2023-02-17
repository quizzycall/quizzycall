from typing import Optional, List
from sqlmodel import Column, Field, SQLModel, Integer
from sqlalchemy.dialects import postgresql


class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    creator_id: Optional[int] = Field(default=None, foreign_key="users.id")
    title: str
    max_points: int
    timeout_id: int = Field(default=None, foreign_key="timeout.id")
    questions_id: List[int] = Field(default=None, sa_column=Column(postgresql.ARRAY(Integer())))
    amount_users: int
    group_id: int = None


class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    answers_id: List[int] = Field(default=None, sa_column=Column(postgresql.ARRAY(Integer())))
    right_answer_id: int = Field(default=None, foreign_key="answer.id")
    amount_points: int


class Answer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str


class TimeOut(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hours: int
    minutes: int
    seconds: int

    def convert_to_secs(self):
        return float(self.hours * 3600 + self.minutes * 60 + self.seconds)
