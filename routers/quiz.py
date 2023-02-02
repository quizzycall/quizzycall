from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Request,  WebSocket, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from typing import Optional
from validation.quiz import Quiz as QuizVal, QuizEdit
from db.quiz import create_quiz, get_quiz_by_id, edit_quiz
from security.jwt import verify_token
from security.oauth import get_current_user
from db.user import get_user_data
from db.quiz_websocket import play_quiz, rooms, session_quiz, session_quiz_creator
from db.settings import get_session
from db.models.quiz import Quiz

quiz_api = APIRouter()
templates = Jinja2Templates(directory='templates')


@quiz_api.post("/create_quiz")
async def create_quiz_url(quiz: QuizVal, login=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await create_quiz(quiz, login, session)


@quiz_api.patch('/edit-quiz/{quiz_id}')
async def edit_quiz_url(quiz_id: int, quiz_edit: QuizEdit, login=Depends(get_current_user),
                        session: AsyncSession = Depends(get_session)):
    return await edit_quiz(quiz_id, quiz_edit, login, session)


@quiz_api.get("/get_quiz/{quiz_id}")
async def get_quiz_url(quiz_id: int, session: AsyncSession = Depends(get_session)):
    return dict(await get_quiz_by_id(quiz_id, session))


@quiz_api.get("/play_quiz/{quiz_id}")
async def play_quiz_url(quiz_id: int, anon: bool, login=Depends(get_current_user),
                        session: AsyncSession = Depends(get_session)):
    return await play_quiz(quiz_id, login, anon, session)


# html routes for test
# --------


@quiz_api.get('/client/session_quiz/{pin}')
async def client_session_quiz_url(req: Request, pin: int, token: Optional[str] = None, nickname: Optional[str] = None):
    if rooms.get(pin):
        return templates.TemplateResponse('index.html', {'request': req, 'pin': pin, 'token': token,
                                                         'nickname': nickname})
    raise HTTPException(status_code=400)


@quiz_api.get('/client/session_quiz_creator/{pin}')
async def client_session_quiz_creator_url(req: Request, pin: int, token: str,
                                          session: AsyncSession = Depends(get_session)):
    user = await get_user_data(verify_token(token), session)
    quiz = await get_quiz_by_id(rooms[pin]['quiz_id'], session)
    if rooms.get(pin) and quiz.creator_id == user.id:
        return templates.TemplateResponse('creator.html', {'request': req, 'pin': pin, 'token': token})
    raise HTTPException(status_code=400)


# --------


@quiz_api.websocket("/session_quiz/{pin}")
async def session_quiz_url(websocket: WebSocket, pin: int, token: Optional[str] = None, nickname: Optional[str] = None,
                           session: AsyncSession = Depends(get_session)):
    await session_quiz(websocket, pin, session, token, nickname)


@quiz_api.websocket("/session_quiz_creator/{pin}")
async def session_quiz_creator_url(websocket: WebSocket, pin: int, token: str,
                                   session: AsyncSession = Depends(get_session)):
    await session_quiz_creator(websocket, pin, token, session)
