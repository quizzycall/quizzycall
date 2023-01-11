from fastapi import APIRouter, Depends
from security.oauth import get_current_user
from validation.group import CreateGroup
from db.group import create_group

group_api = APIRouter()


@group_api.post('/create-group')
async def create(group: CreateGroup, login=Depends(get_current_user)):
    return create_group(login, group)
