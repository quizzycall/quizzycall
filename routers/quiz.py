from fastapi import APIRouter, Response, WebSocket
from typing import List
from validation.quiz import Quiz
from db.quiz import create_quiz, get_quiz_by_id, start_quiz
from security.jwt import verify_token
from db.user import get_user_data

quiz_api = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

rooms = {}

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

@quiz_api.get("/create_room/{id}")
async def create_room_url(id: int, token: str):
    quiz = get_quiz_by_id(id)
    id_user = get_user_data(verify_token(token)).id
    if quiz and quiz.creator_id == id_user:
        rooms[id] = ConnectionManager()
        return Response("Good create!", 200)
    else:
        return Response("You are not creator", 403)

@quiz_api.post("/start_quiz/{id}")
async def start_quiz_url(id: int, token: str):
    quiz = get_quiz_by_id(id)
    id_user = get_user_data(verify_token(token)).id
    if quiz and quiz.creator_id == id_user:
        start_quiz(id)
        
@quiz_api.websocket("/session_quiz/{id}")
async def session_quiz_url(websocket: WebSocket, id: int, token: str):
    if rooms.get(id) and get_quiz_by_id(id):
        manager = rooms.get(id)
        manager.connect(websocket)
        
        manager.broadcast({"message": f"User {websocket} connected!", "amount_questions": len(get_quiz_by_id(id).questions_id)})
