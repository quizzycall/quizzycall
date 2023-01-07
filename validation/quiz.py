from typing import Optional
from pydantic import BaseModel
from datetime import date, datetime, time, timedelta

class AnswerOption(BaseModel):
    answer: str

class Question(BaseModel):
    title: str
    answer_options: list[AnswerOption]
    right_answer: str
    amount_points: int

class TimeOut(BaseModel):
    hours: int
    minutes: int
    seconds: int

class Quiz(BaseModel):
    creator_id: int
    title: str
    timeout: TimeOut
    questions: list[Question]
    max_points: int
    amount_users: int
    start: bool = False


