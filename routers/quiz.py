import json
import random
from asyncio import wait_for
from asyncio.exceptions import TimeoutError
import traceback
from fastapi import APIRouter, Request, Response, WebSocket, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool
from typing import List, Dict
from validation.quiz import Quiz
from db.quiz import create_quiz, get_quiz_by_id, start_quiz, query_to_dict, prepare_question, sum_points, get_timeout_by_id
from security.jwt import verify_token
from security.oauth import get_current_user
from db.user import get_user_data

quiz_api = APIRouter()
templates = Jinja2Templates(directory='templates')


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._answers: Dict[str, list] = {}
        self._points: Dict[str, int] = {}

    @property
    def points(self):
        return self._points

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    def append_answer(self, answer: str, websocket: WebSocket, nickname: str, user_id: int):
        if not self._answers.get(answer):
            self._answers[answer] = [{'user_id': user_id, 'nickname': nickname, 'websocket': websocket}]
        else:
            self._answers[answer].append({'user_id': user_id, 'nickname': nickname, 'websocket': websocket})

    async def right_answer_and_results(self, answer: str, points: int):
        for a, v in self._answers.items():
            for connection in v:
                if a == answer:
                    if not self._points.get(connection['nickname']):
                        self._points[connection['nickname']] = points
                    else:
                        self._points[connection['nickname']] += points
                    await connection['websocket'].send_json(
                        f'right answer, +{points} points. now you have {self._points[connection["nickname"]]} points'
                    )
                else:
                    await connection['websocket'].send_json('wrong answer')
                del connection['websocket']
        await self.broadcast({'question_results': self._answers, 'points': self._points})
        self._answers.clear()

    async def finish_quiz(self, pin: int):
        await self.broadcast({'msg': 'quiz finished', 'points': self._points})
        await run_in_threadpool(sum_points, self._points)
        del rooms[pin]

    async def broadcast(self, data):
        if len(self.active_connections) > 0:
            for connection in self.active_connections:
                await connection.send_json(data)

    async def broadcast_to_players(self, data, creator_websocket: WebSocket):
        if len(self.active_connections) > 0:
            for connection in self.active_connections:
                if connection != creator_websocket:
                    await connection.send_json(data)


rooms: Dict[int, dict] = {}


async def get_pin():
    while True:
        pin = random.randint(100000, 999999)
        if pin not in rooms:
            return pin


@quiz_api.post("/create_quiz")
async def create_quiz_url(quiz: Quiz, login=Depends(get_current_user)):
    creator_id = get_user_data(login).id
    quiz = dict(quiz)
    quiz["creator_id"] = creator_id
    return create_quiz(quiz)


@quiz_api.get("/get_quiz/{id}")
async def get_quiz_url(quiz_id: int, login=Depends(get_current_user)):
    # if login:
    #     return dict(get_quiz_by_id(quiz_id))
    # else:
    #     return Response("You are not logged in", 400)
    return dict(get_quiz_by_id(quiz_id))


@quiz_api.get("/play_quiz/{id}")
async def play_quiz(quiz_id: int, login=Depends(get_current_user)):
    quiz = get_quiz_by_id(quiz_id)
    id_user = get_user_data(login).id
    if quiz and quiz.creator_id == id_user:
        pin = await get_pin()
        rooms[pin] = {'manager': ConnectionManager(), 'quiz_id': quiz_id}
        return Response(json.dumps({'pin_code': pin}), 200)
    else:
        raise HTTPException(detail="You are not creator", status_code=403)

# @quiz_api.get("/create_room/{id}")
# async def create_room_url(quiz_id: int, login=Depends(get_current_user)):
#     quiz = get_quiz_by_id(quiz_id)
#     id_user = get_user_data(login).id
#     if quiz and quiz.creator_id == id_user:
#         rooms[quiz_id] = ConnectionManager()
#         return Response("Good create!", 200)
#     else:
#         raise HTTPException(detail="You are not creator", status_code=403)
#
#
# @quiz_api.post("/start_quiz/{id}")
# async def start_quiz_url(quiz_id: int, login=Depends(get_current_user)):
#     quiz = get_quiz_by_id(quiz_id)
#     id_user = get_user_data(login).id
#     if quiz and quiz.creator_id == id_user:
#         start_quiz(quiz_id)


# html routes for test
# --------
@quiz_api.get('/client/session_quiz/{pin}')
async def client_session_quiz_url(req: Request, pin: int, token: str):
    if rooms.get(pin):
        return templates.TemplateResponse('index.html', {'request': req, 'pin': pin, 'token': token})
    raise HTTPException(status_code=400)


@quiz_api.get('/client/session_quiz_creator/{pin}')
async def client_session_quiz_creator_url(req: Request, pin: int, token: str):
    user = get_user_data(verify_token(token))
    if rooms.get(pin) and get_quiz_by_id(rooms[pin]['quiz_id']).creator_id == user.id:
        return templates.TemplateResponse('creator.html', {'request': req, 'pin': pin, 'token': token})
    raise HTTPException(status_code=400)
# --------


@quiz_api.websocket("/session_quiz/{pin}")
async def session_quiz_url(websocket: WebSocket, pin: int, token: str):
    user = get_user_data(verify_token(token))
    manager = rooms[pin]['manager']
    await manager.connect(websocket)
    await manager.broadcast({"message": f"User {user.nickname} connected!",
                             "amount_questions": len(get_quiz_by_id(rooms[pin]['quiz_id']).questions_id)})
    try:
        while True:
            data_wb = await websocket.receive_json()
            if data_wb.get('answer'):
                manager.append_answer(data_wb['answer']['title'], websocket, user.nickname, user.id)
    except:
        manager.disconnect(websocket)
        await manager.broadcast({"message": f"User {user.nickname} disconnected!"})


@quiz_api.websocket("/session_quiz_creator/{pin}")
async def session_quiz_creator_url(websocket: WebSocket, pin: int, token: str):
    user = get_user_data(verify_token(token))
    manager = rooms[pin]['manager']
    quiz_id = rooms[pin]['quiz_id']
    await manager.connect(websocket)
    try:
        while True:
            data_wb = await websocket.receive_json()
            if data_wb.get('msg_creator') == 'started':
                start_quiz(quiz_id)
                await manager.broadcast({'msg': 'started'})
                break
        quiz = query_to_dict(get_quiz_by_id(quiz_id))

        async def quiz_func():
            for q in quiz['questions_id']:
                question = prepare_question(q)
                await manager.broadcast({'question': question})
                while True:
                    data_wb = await websocket.receive_json()
                    if data_wb.get('msg_creator') == 'skip':
                        await manager.right_answer_and_results(question['right_answer']['title'],
                                                               question['amount_points'])
                    elif data_wb.get('msg_creator') == 'next':
                        break
        timeout = get_timeout_by_id(quiz['timeout_id']).convert_to_secs()
        await wait_for(quiz_func(), timeout=timeout)
        await manager.finish_quiz(pin)
    except TimeoutError:
        await manager.broadcast('timeout')
        await manager.finish_quiz(pin)
    except:
        print(traceback.format_exc())
        manager.disconnect(websocket)
        await manager.broadcast({"message": f"User {user.nickname} disconnected!"})
