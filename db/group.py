from sqlalchemy.orm.attributes import flag_modified
from fastapi import HTTPException
from sqlmodel import select
from validation.group import CreateGroup, GroupUsers
from .user import get_user_data
from .models.group import Group
from sqlalchemy.ext.asyncio import AsyncSession


async def create_group(login: str, group: CreateGroup, session: AsyncSession):
    user = await get_user_data(login, session)
    group_db = Group(name=group.name, creator_id=user.id, description=group.description, participants_id=group.users)
    session.add(group_db)
    await session.flush()
    await session.refresh(group_db)
    for nickname in group.users:
        _u = await get_user_data(nickname, session)
        if not _u:
            raise HTTPException(status_code=400, detail=f'No such user with nickname {nickname}')
        _u.groups_id.append(group_db.id)
        flag_modified(_u, 'groups_id')
        group_db.participants_id.append(user.id)
    flag_modified(group_db, 'participants_id')
    user.groups_id.append(group_db.id)
    flag_modified(user, 'groups_id')
    await session.commit()
    return {'group_id': group_db.id}


async def get_group_by_id(group_id: int, session: AsyncSession) -> Group:
    r = await session.execute(select(Group).where(Group.id == group_id))
    return r.scalar_one_or_none()


async def add_users(users: GroupUsers, group_id: int, login: str, session: AsyncSession):
    group = await get_group_by_id(group_id, session)
    _u = await get_user_data(login, session)
    if group and group.creator_id == _u.id:
        for nickname in users.users:
            user = await get_user_data(nickname, session)
            if not user:
                raise HTTPException(status_code=400, detail=f'No such user with nickname {nickname}')
            user.groups_id.append(group_id)
            flag_modified(user, 'groups_id')
            group.participants_id.append(user.id)
        flag_modified(group, 'participants_id')
        await session.commit()
        return True
    raise HTTPException(status_code=400, detail='No group with such id')


async def delete_users(users: GroupUsers, group_id: int, login: str, session: AsyncSession):
    group = await get_group_by_id(group_id, session)
    _u = await get_user_data(login, session)
    if group and group.creator_id == _u.id:
        for nickname in users.users:
            user = await get_user_data(nickname, session)
            if not user:
                raise HTTPException(status_code=400, detail=f'No such user with nickname {nickname}')
            if group_id not in user.groups_id:
                raise HTTPException(status_code=400, detail=f'{nickname} is not in your group')
            user.groups_id.remove(group_id)
            flag_modified(user, 'groups_id')
            group.participants_id.remove(user.id)
        flag_modified(group, 'participants_id')
        await session.commit()
        return True
    raise HTTPException(status_code=400, detail="No group with such id or you're not a creator")

