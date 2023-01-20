from fastapi import APIRouter, Request, Response, WebSocket, Depends
import json
from starlette.websockets import WebSocketClose, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from typing import List
from validation.quiz import Quiz
from db.quiz import create_quiz, get_quiz_by_id, start_quiz
from security.jwt import verify_token
from security.oauth import get_current_user
from db.user import get_user_data

quiz_api = APIRouter()
templates = Jinja2Templates(directory='templates')


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
        if len(self.active_connections) > 0:
            for connection in self.active_connections:
                await connection.send_json(message)


rooms = {}


@quiz_api.post("/create_quiz")
async def create_quiz_url(quiz: Quiz, login=Depends(get_current_user)):
    creator_id = get_user_data(login).id
    quiz = dict(quiz)
    quiz["creator_id"] = creator_id
    return create_quiz(quiz)


@quiz_api.get("/get_quiz/{id}")
async def get_quiz_url(id: int, login=Depends(get_current_user)):
    if login:
        return dict(get_quiz_by_id(id))
    else:
        return Response("You are not logged in", 400)


@quiz_api.get("/create_room/{id}")
async def create_room_url(id: int, login=Depends(get_current_user)):
    quiz = get_quiz_by_id(id)
    id_user = get_user_data(login).id
    if quiz and quiz.creator_id == id_user:
        rooms[id] = ConnectionManager()
        return Response("Good create!", 200)
    else:
        return Response("You are not creator", 403)


@quiz_api.post("/start_quiz/{id}")
async def start_quiz_url(id: int, login=Depends(get_current_user)):
    quiz = get_quiz_by_id(id)
    id_user = get_user_data(login).id
    if quiz and quiz.creator_id == id_user:
        start_quiz(id)


# html routes for test
# --------
@quiz_api.get('/client/session_quiz/{id}')
async def client_session_quiz_url(req: Request, id: int, token: str):
    return templates.TemplateResponse('index.html', {'request': req, 'id': id, 'token': token})


@quiz_api.get('/client/session_quiz_creator/{id}')
async def client_session_quiz_creator_url(req: Request, id: int, token: str):
    return templates.TemplateResponse('creator.html', {'request': req, 'id': id, 'token': token})
# --------


@quiz_api.websocket("/session_quiz/{id}")
async def session_quiz_url(websocket: WebSocket, id: int, token: str):
    if rooms.get(id) and get_quiz_by_id(id):
        user = get_user_data(verify_token(token))
        manager = rooms.get(id)
        await manager.connect(websocket)
        await manager.broadcast({"message": f"User {user.nickname} connected!",
                                 "amount_questions": len(get_quiz_by_id(id).questions_id)})
        try:
            while True:
                data_wb = await websocket.receive_text()
                data_wb = json.loads(data_wb)
                await manager.broadcast(data_wb)
        except:
            manager.disconnect(websocket)
            await manager.broadcast({"message": f"User {user.nickname} disconnected!"})


@quiz_api.websocket("/session_quiz_creator/{id}")
async def session_quiz_creator_url(websocket: WebSocket, id: int, token: str):
    # print(verify_token(token))
    # if rooms.get(id) and get_quiz_by_id(id):
    #     user = get_user_data(verify_token(token))
    #     print(rooms)
    #     manager = rooms.get(id)
    #     await manager.connect(websocket)
    #
    #     await manager.broadcast({"message": f"User {user.nickname} connected!",
    #                              "amount_questions": len(get_quiz_by_id(id).questions_id)})
    #     try:
    #         while True:
    #             data_wb = await websocket.receive_text()
    #             data_wb = json.loads(data_wb)
    #             await manager.broadcast(data_wb)
    #     except Exception as e:
    #         print(e, 5676)
    #         manager.disconnect(websocket)
    #         await manager.broadcast({"message": f"User {user.nickname} disconnected!"})
    pass
