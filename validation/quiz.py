from typing import Optional, List
from pydantic import BaseModel
from datetime import date, datetime, time, timedelta

class AnswerOption(BaseModel):
    title: str
    is_right: bool = False


class Question(BaseModel):
    title: str
    answer_options: list[AnswerOption]
    amount_points: int


class TimeOut(BaseModel):
    hours: int
    minutes: int
    seconds: int


class TimeOutEdit(BaseModel):
    hours: Optional[int] = None
    minutes: Optional[int] = None
    seconds: Optional[int] = None


class Quiz(BaseModel):
    creator_id: int = None
    group_id: int = None
    title: str
    timeout: TimeOut
    questions: list[Question]
    max_points: int
    amount_users: int
    start: bool = False


class AnswerOptionEdit(AnswerOption):
    id: int
    title: Optional[str] = None
    is_right: Optional[bool] = None


class QuestionEdit(BaseModel):
    title: Optional[str] = None
    answer_options: Optional[list[AnswerOptionEdit]] = None
    amount_points: Optional[int] = None
    right_answer_id: Optional[int] = None


class QuizEdit(BaseModel):
    title: Optional[str] = None
    timeout: Optional[TimeOutEdit] = None
    questions: Optional[list[QuestionEdit]] = None
    max_points: Optional[int] = None
    amount_users: Optional[int] = None


class QuestionWebSocketResponse(BaseModel):
    id: int
    title: str
    answers: List[AnswerOption]


class QuizWebSocketResponse(BaseModel):
    id: int
    creator_id: int
    title: str
    questions: List[QuestionWebSocketResponse]
