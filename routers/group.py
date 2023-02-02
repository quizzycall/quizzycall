from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from security.oauth import get_current_user
from validation.group import CreateGroup
from db.group import create_group, add_users, delete_users, get_group_by_id
from validation.group import GroupUsers
from db.quiz import change_group_id
from db.settings import get_session

group_api = APIRouter()


@group_api.post('/create-group')
async def create(group: CreateGroup, login=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await create_group(login, group, session)


@group_api.get('/get-group/{group_id}')
async def get_group(group_id: int, session: AsyncSession = Depends(get_session)):
    return await get_group_by_id(group_id, session)


@group_api.patch('/add-to-group/{group_id}')
async def add_users_to_group(group_id: int, users: GroupUsers, login=Depends(get_current_user),
                             session: AsyncSession = Depends(get_session)):
    return await add_users(users, group_id, login, session)


@group_api.patch('/delete-from-group/{group_id}')
async def delete_users_from_group(group_id: int, users: GroupUsers, login=Depends(get_current_user),
                                  session: AsyncSession = Depends(get_session)):
    return await delete_users(users, group_id, login, session)


# @group_api.post("/create-quiz")
# async def create_quiz(quiz: Quiz, group_id: int, login=Depends(get_current_user),
#                       session: AsyncSession = Depends(get_session)):
#     _u = await get_user_data(login, session)
#     creator_id = _u.id
#     quiz = dict(quiz)
#     quiz["creator_id"] = creator_id
#     return create_quiz(quiz, group_id=group_id)


@group_api.patch("/change-group-id-of-quiz/{group_id}/{quiz_id}")
async def change_group_id_of_quiz(group_id: int, quiz_id: int, login=Depends(get_current_user),
                                  session: AsyncSession = Depends(get_session)):
    return await change_group_id(group_id, quiz_id, login, session)
