from sqlalchemy.orm.attributes import flag_modified
from validation.group import CreateGroup
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
