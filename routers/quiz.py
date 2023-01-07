from fastapi import APIRouter
from validation.quiz import Quiz
from db.quiz import CreateQuiz

quiz_api = APIRouter()

@quiz_api.post("/create_quiz")
async def create_quiz(quiz: Quiz):
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


    return CreateQuiz(quiz)