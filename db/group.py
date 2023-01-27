from sqlalchemy.orm.attributes import flag_modified
from fastapi import HTTPException
from sqlmodel import select
from validation.group import CreateGroup, GroupUsers
from .user import get_user_data
from .models.group import Group
from .settings import session


def create_group(login: str, group: CreateGroup):
    user = get_user_data(login)
    group_db = Group(name=group.name, creator_id=user.id, description=group.description)
    session.add(group_db)
    session.flush()
    session.refresh(group_db)
    user.groups_id.append(group_db.id)
    flag_modified(user, 'groups_id')
    session.commit()
    return group_db.id


def get_group_by_id(group_id: int):
    return session.exec(select(Group).where(Group.id == group_id)).first()


def add_users(users: GroupUsers, group_id: int, login: str):
    group = get_group_by_id(group_id)
    if group and group.creator_id == get_user_data(login).id:
        for nickname in users.users:
            user = get_user_data(nickname)
            if not user:
                raise HTTPException(status_code=400, detail=f'No such user with nickname "{nickname}"')
            user.groups_id.append(group_id)
            flag_modified(user, 'groups_id')
            group.participants_id.append(user.id)
        flag_modified(group, 'participants_id')
        session.commit()
        return True
    raise HTTPException(status_code=400, detail='No group with such id')


def delete_users(users: GroupUsers, group_id: int, login: str):
    group = get_group_by_id(group_id)
    if group and group.creator_id == get_user_data(login).id:
        for nickname in users.users:
            user = get_user_data(nickname)
            if not user:
                raise HTTPException(status_code=400, detail=f'No such user with nickname "{nickname}"')
            user.groups_id.remove(group_id)
            flag_modified(user, 'groups_id')
            group.participants_id.remove(user.id)
        flag_modified(group, 'participants_id')
        session.commit()
        return True
    raise HTTPException(status_code=400, detail="No group with such id or you're not a creator")

