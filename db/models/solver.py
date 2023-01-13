from sqlmodel import SQLModel, Field
from db.models.user import Users
from db.models.quiz import Quiz

class Solver(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="users.id")
    quiz_id: int = Field(default=None, foreign_key="quiz.id")
    points: int = 0