from typing import Optional
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

class Quiz(BaseModel):
    creator_id: int = None
    title: str
    timeout: TimeOut
    questions: list[Question]
    max_points: int
    amount_users: int
    start: bool = False


