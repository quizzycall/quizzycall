from fastapi import APIRouter, Depends
from validation.quiz import Quiz
from db.quiz import create_quiz
from security.jwt import verify_token
from db.user import get_user_data

quiz_api = APIRouter()

@quiz_api.post("/create_quiz")
async def create_quiz_url(quiz: Quiz, token: str):
    """
{
  "creator_id": 0,
  "title": "string",
  "timeout": {
    "hours": 0,
    "minutes": 0,
    "seconds": 0
  },
  "questions": [
    {
      "title": "string",
      "answer_options": [
        {
          "answer": "string"
        }
      ],
      "right_answer_id": 0,
      "amount_points": 0
    }
  ],
  "max_points": 0,
  "amount_users": 0,
  "start": false
}
    """
    creator_id = get_user_data(verify_token(token)).id
    quiz = dict(quiz)
    quiz["creator_id"] = creator_id
    return create_quiz(quiz)