from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from db.models.user import Users

class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    creator_id: Optional[int] = Field(default=None, foreign_key="users.id")
    title: str
    max_points: int
    timeout_id: int = Field(default=None, foreign_key="timeout.id")
    questions: List["Question"] = Relationship(back_populates="quiz")
    start: bool = False
    amount_users: int

class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    answers: List["Answer"] = Relationship(back_populates="question")
    quiz: Optional[Quiz] = Relationship(back_populates="questions")
    right_answer_id: int = Field(default=None, foreign_key="answer.id")
    amount_points: int

class Answer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question: Optional[Question] = Relationship(back_populates="answers")
    title: str

class TimeOut(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hours: int
    minutes: int
    seconds: int