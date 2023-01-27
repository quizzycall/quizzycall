from fastapi import APIRouter, Depends
from security.oauth import get_current_user
from validation.group import CreateGroup
from db.group import create_group, add_users, delete_users
from validation.quiz import Quiz
from validation.group import GroupUsers
from db.user import get_user_data
from db.quiz import change_group_id

group_api = APIRouter()


@group_api.post('/create-group')
async def create(group: CreateGroup, login=Depends(get_current_user)):
    return create_group(login, group)


@group_api.post('/add-to-group')
async def add_users_to_group(group_id: int, users: GroupUsers, login=Depends(get_current_user)):
    return add_users(users, group_id, login)


@group_api.post('/delete-from-group')
async def delete_users_from_group(group_id: int, users: GroupUsers, login=Depends(get_current_user)):
    return delete_users(users, group_id, login)


@group_api.post("/create-quiz")
async def create_quiz(quiz: Quiz, group_id: int, login=Depends(get_current_user)):
    creator_id = get_user_data(login).id
    quiz = dict(quiz)
    quiz["creator_id"] = creator_id
    return create_quiz(quiz, group_id=group_id)


@group_api.post("/change-group-id")
async def change_group_id_of_quiz(quiz_id: int, group_id: int, login=Depends(get_current_user)):
    return change_group_id(group_id, quiz_id, login)
