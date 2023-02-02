import json
from asyncio import wait_for
from asyncio.exceptions import TimeoutError
from sqlalchemy.ext.asyncio import AsyncSession
import traceback
from fastapi import Response, WebSocket, HTTPException
from starlette.concurrency import run_in_threadpool
from typing import List, Dict, Optional
from db.quiz import get_quiz_by_id, start_quiz, query_to_dict, prepare_question, sum_points, get_timeout_by_id, get_pin
from security.jwt import verify_token
from db.user import get_user_data


class ConnectionManager:
    def __init__(self, amount_users: int):
        self.amount_users = amount_users
        self.active_connections: List[WebSocket] = []
        self._answers: Dict[str, list] = {}
        self._points: Dict[str, int] = {}

    @property
    def points(self):
        return self._points

    async def connect(self, websocket: WebSocket):
        if len(self.active_connections) >= self.amount_users + 1:
            raise HTTPException(400, 'Game is full.')
        else:
            await websocket.accept()
            self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    def append_answer(self, answer: str, websocket: WebSocket, nickname: str, anon: bool,
                      user_id: Optional[int] = None):
        if anon:
            ans_dict = {'nickname': nickname, 'websocket': websocket}
        else:
            ans_dict = {'user_id': user_id, 'nickname': nickname, 'websocket': websocket}
        if not self._answers.get(answer):
            self._answers[answer] = [ans_dict]
        else:
            self._answers[answer].append(ans_dict)

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
        if not rooms[pin]['anon']:
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


async def play_quiz(quiz_id: int, login: str, anon: bool, session: AsyncSession):
    quiz = await get_quiz_by_id(quiz_id, session)
    _u = await get_user_data(login, session)
    id_user = _u.id
    if quiz and quiz.creator_id == id_user:
        pin = await get_pin(rooms)
        rooms[pin] = {'manager': ConnectionManager(quiz.amount_users), 'quiz_id': quiz_id, 'anon': anon}
        return Response(json.dumps({'pin_code': pin}), 200)
    else:
        raise HTTPException(detail="You are not creator", status_code=403)


async def session_quiz(websocket: WebSocket, pin: int, session: AsyncSession, token: Optional[str] = None,
                       nickname: Optional[str] = None):
    manager = rooms[pin]['manager']
    quiz = await get_quiz_by_id(rooms[pin]['quiz_id'], session)
    if token and not rooms[pin]['anon']:
        user = await get_user_data(verify_token(token), session)
        await manager.connect(websocket)
        await manager.broadcast({"message": f"User {user.nickname} connected!",
                                 "amount_questions": len(quiz.questions_id)})
        try:
            while True:
                data_wb = await websocket.receive_json()
                if data_wb.get('answer'):
                    manager.append_answer(data_wb['answer']['title'], websocket, user.nickname, user.id)
        except:
            manager.disconnect(websocket)
            await manager.broadcast({"message": f"User {user.nickname} disconnected!"})
    elif nickname and rooms[pin]['anon']:
        await manager.connect(websocket)
        await manager.broadcast({"message": f"User {nickname} connected!",
                                 "amount_questions": len(quiz.questions_id)})
        try:
            while True:
                data_wb = await websocket.receive_json()
                if data_wb.get('answer'):
                    manager.append_answer(data_wb['answer']['title'], websocket, nickname, anon=True)
        except:
            manager.disconnect(websocket)
            await manager.broadcast({"message": f"User {nickname} disconnected!"})


async def session_quiz_creator(websocket: WebSocket, pin: int, token: str, session: AsyncSession):
    user = await get_user_data(verify_token(token), session)
    manager = rooms[pin]['manager']
    quiz_id = rooms[pin]['quiz_id']
    await manager.connect(websocket)
    try:
        while True:
            data_wb = await websocket.receive_json()
            if data_wb.get('msg_creator') == 'started':
                await start_quiz(quiz_id, session)
                await manager.broadcast({'msg': 'started'})
                break
        quiz = query_to_dict(await get_quiz_by_id(quiz_id, session))

        async def quiz_func():
            for q in quiz['questions_id']:
                question = await prepare_question(q, session)
                await manager.broadcast({'question': question})
                while True:
                    data_wb = await websocket.receive_json()
                    if data_wb.get('msg_creator') == 'skip':
                        await manager.right_answer_and_results(question['right_answer']['title'],
                                                               question['amount_points'])
                    elif data_wb.get('msg_creator') == 'next':
                        break

        _t = await get_timeout_by_id(quiz['timeout_id'], session)
        timeout = _t.convert_to_secs()
        await wait_for(quiz_func(), timeout=timeout)
        await manager.finish_quiz(pin)
    except TimeoutError:
        await manager.broadcast('timeout')
        await manager.finish_quiz(pin)
    except:
        print(traceback.format_exc())
        manager.disconnect(websocket)
        await manager.broadcast({"message": f"User {user.nickname} disconnected!"})
