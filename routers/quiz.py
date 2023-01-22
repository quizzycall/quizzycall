import traceback

from fastapi import APIRouter, Request, Response, WebSocket, Depends, HTTPException
import json
from starlette.websockets import WebSocketClose, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from typing import List, Dict
from validation.quiz import Quiz
from db.quiz import create_quiz, get_quiz_by_id, start_quiz, query_to_dict, prepare_question, results_of_question
from security.jwt import verify_token
from security.oauth import get_current_user
from db.user import get_user_data

quiz_api = APIRouter()
templates = Jinja2Templates(directory='templates')


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.answers: List[dict] = []
        self.points: Dict[str, int] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_text(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_json(self, data: dict, websocket: WebSocket):
        await websocket.send_json(data)

    def append_answer(self, answer: dict, websocket: WebSocket, nickname: str):
        self.answers.append({'nickname': nickname, 'answer': answer, 'websocket': websocket})

    async def right_answer_and_results(self, answer: dict, points: int):
        question_results = results_of_question(self.answers)
        await self.broadcast(data=question_results)
        for connection in self.answers:
            if connection['answer'] == answer:
                if not self.points.get(connection['nickname']):
                    self.points[connection['nickname']] = points
                else:
                    self.points[connection['nickname']] += points
                await connection['websocket'].send_json(
                    f'right answer, +{points} points. now you have {self.points[connection["nickname"]]} points'
                )
            else:
                await connection['websocket'].send_json('wrong answer')
        self.answers.clear()

    async def finish_quiz(self):
        await self.broadcast({'msg': 'quiz finished', 'points': self.points})


    async def broadcast(self, data):
        if len(self.active_connections) > 0:
            for connection in self.active_connections:
                await connection.send_json(data)

    async def broadcast_to_players(self, data, creator_websocket: WebSocket):
        if len(self.active_connections) > 0:
            for connection in self.active_connections:
                if connection != creator_websocket:
                    await connection.send_json(data)


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
    if rooms.get(id) and get_quiz_by_id(id):
        return templates.TemplateResponse('index.html', {'request': req, 'id': id, 'token': token})
    raise HTTPException(status_code=400)


@quiz_api.get('/client/session_quiz_creator/{id}')
async def client_session_quiz_creator_url(req: Request, id: int, token: str):
    user = get_user_data(verify_token(token))
    if rooms.get(id) and get_quiz_by_id(id).creator_id == user.id:
        return templates.TemplateResponse('creator.html', {'request': req, 'id': id, 'token': token})
    raise HTTPException(status_code=400)
# --------


@quiz_api.websocket("/session_quiz/{id}")
async def session_quiz_url(websocket: WebSocket, id: int, token: str):
    user = get_user_data(verify_token(token))
    manager = rooms.get(id)
    await manager.connect(websocket)
    await manager.broadcast({"message": f"User {user.nickname} connected!",
                             "amount_questions": len(get_quiz_by_id(id).questions_id)})
    try:
        while True:
            data_wb = await websocket.receive_json()
            if data_wb.get('answer'):
                print(data_wb['answer'])
                manager.append_answer(data_wb['answer'], websocket, user.nickname)

    except:
        manager.disconnect(websocket)
        await manager.broadcast({"message": f"User {user.nickname} disconnected!"})


@quiz_api.websocket("/session_quiz_creator/{id}")
async def session_quiz_creator_url(websocket: WebSocket, id: int, token: str):
    user = get_user_data(verify_token(token))
    manager = rooms.get(id)
    await manager.connect(websocket)
    try:
        while True:
            data_wb = await websocket.receive_json()
            if data_wb.get('msg_creator') == 'started':
                start_quiz(id)
                await manager.broadcast({'msg': 'started'})
                break

        quiz = query_to_dict(get_quiz_by_id(id))
        for q in quiz['questions_id']:
            question = prepare_question(q)
            await manager.send_json(question, websocket)
            await manager.broadcast_to_players({'question': question}, websocket)
            while True:
                data_wb = await websocket.receive_json()
                if data_wb.get('msg_creator') == 'skip':
                    await manager.right_answer_and_results(question['right_answer'], question['amount_points'])
                elif data_wb.get('msg_creator') == 'next':
                    break
        await manager.finish_quiz()

    except:
        print(traceback.format_exc(), 89898)
        manager.disconnect(websocket)
        await manager.broadcast({"message": f"User {user.nickname} disconnected!"})





    # try:
    #     while True:
    #         data_wb = await websocket.receive_text()
    #         data_wb = json.loads(data_wb)
    #         await manager.broadcast(data_wb)
    # except Exception as e:
    #     print(e, 5676)
    #     manager.disconnect(websocket)
    #     await manager.broadcast({"message": f"User {user.nickname} disconnected!"})
