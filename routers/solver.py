from fastapi import APIRouter, Response
from db.quiz import get_quiz_by_id, get_question_by_id, get_answer_by_id
from security.jwt import verify_token

solver_api = APIRouter()

@solver_api.get("/get_questions/{quiz_id}/{questions_position}")
async def get_questions(quiz_id: int, questions_position: int, token: str):
    if verify_token(token):
        quiz = get_quiz_by_id(quiz_id)
        questions = get_question_by_id(quiz.questions_id[questions_position])
        return questions.json()
    else: 
        return Response("You are not logged in!", 400)