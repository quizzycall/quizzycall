from fastapi import APIRouter, Response
from validation.quiz import Quiz
from db.quiz import create_quiz, get_quiz_by_id, start_quiz
from security.jwt import verify_token
from db.user import get_user_data

quiz_api = APIRouter()


@quiz_api.post("/create_quiz")
async def create_quiz_url(quiz: Quiz, token: str):
    creator_id = get_user_data(verify_token(token)).id
    quiz = dict(quiz)
    quiz["creator_id"] = creator_id
    return create_quiz(quiz)

@quiz_api.get("/get_quiz/{id}")
async def get_quiz_url(id: int, token: str):
	if verify_token(token):
		return dict(get_quiz_by_id(id))
	else:
		return Response("You are not logged in", 400)


@quiz_api.post("/start_quiz/{id}")
async def start_quiz_url(id: int, token: str):
    quiz = get_quiz_by_id(id)
    id_user = get_user_data(verify_token(token)).id
    if quiz and quiz.creator_id == id_user:
        start_quiz(id)
        