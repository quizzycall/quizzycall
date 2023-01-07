from typing import Optional
from sqlmodel import Field, SQLModel
from validation.quiz import TimeOut
from db.models.user import Users

class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    creator_id: Optional[int] = Field(default=None, foreign_key="users.id")
    title: str
    max_points: int
    timeout_id: int = Field(default=None, foreign_key="timeout.id")
    questions_id: list[int] = list[Field(default=None, foreign_key="question.id")]
    start: bool = False
    amount_users: int

class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    answers_id: list[int] = list[Field(default=None, foreign_key="answer.id")]
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