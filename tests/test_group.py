import pytest
from httpx import AsyncClient
from validation.group import CreateGroup, GroupUsers
from db.group import get_group_by_id
from db.user import get_user_data
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.parametrize('group_data, token',
                         [
                             (CreateGroup(
                                 name='group1',
                                 description='desc',
                                 users=['2']), 'user_2_token'),
                             (CreateGroup(
                                 name='group2',
                                 description='desc',
                                 users=['2']), 'token'),
                             (CreateGroup(
                                 name='group1',
                                 description='desc',
                                 users=['2']), 'user_2_token')
                         ])
async def test_create(ac: AsyncClient, session: AsyncSession, group_data, token):
    ac.headers["content-type"] = 'application/json'
    ac.headers['Authorization'] = f"Bearer {ac.headers.get(token)}"
    res = await ac.post('/api/group/create-group', json=group_data.dict())
    assert res.status_code == 200
    group = await get_group_by_id(res.json()['group_id'], session)
    user = await get_user_data('2', session)
    assert group.name == group_data.name
    assert group.description == group_data.description
    assert 2 in group.participants_id
    assert res.json()['group_id'] in user.groups_id


async def test_create_error(ac: AsyncClient):
    ac.headers['Authorization'] = f"Bearer {ac.headers.get('token')}"
    group_data = CreateGroup(
        name='group3',
        description='desc',
        users=['3893939']  # non-existing user
    )
    res = await ac.post('/api/group/create-group', json=group_data.dict())
    assert res.status_code == 400


async def test_get_group(ac: AsyncClient):
    res = await ac.get('/api/group/get-group/1')
    assert res.status_code == 200


async def test_get_group_error(ac: AsyncClient):
    res = await ac.get('/api/group/get-group/13939')  # non-existing group
    assert res.status_code == 404


async def test_add_users_to_group(ac: AsyncClient, session: AsyncSession):
    res = await ac.patch('/api/group/add-to-group/2', json=GroupUsers(users=['3']).dict())
    assert res.status_code == 200
    group = await get_group_by_id(2, session)
    user = await get_user_data('3', session)
    assert 3 in group.participants_id
    assert 2 in user.groups_id


@pytest.mark.parametrize('users, group_id, token, code', [
    (GroupUsers(users=['3']), 2, 'token', 400),  # already existing user
    (GroupUsers(users=['3893']), 2, 'token', 400),  # non-existing user
    (GroupUsers(users=['4']), 2, 'user_2_token', 403),  # not a creator
    (GroupUsers(users=['4']), 393, 'token', 404),  # non-existing group
])
async def test_add_users_to_group_error(ac: AsyncClient, users, group_id, token, code):
    ac.headers['Authorization'] = f"Bearer {ac.headers.get(token)}"
    res = await ac.patch(f'/api/group/add-to-group/{group_id}', json=users.dict())
    assert res.status_code == code


async def test_delete_users_from_group(ac: AsyncClient, session: AsyncSession):
    res = await ac.patch('/api/group/delete-from-group/2', json=GroupUsers(users=['3']).dict())
    assert res.status_code == 200
    group = await get_group_by_id(2, session)
    user = await get_user_data('3', session)
    assert 3 not in group.participants_id
    assert 2 not in user.groups_id


@pytest.mark.parametrize('users, group_id, token, code', [
    (GroupUsers(users=['3']), 2, 'token', 400),  # already existing user
    (GroupUsers(users=['3893']), 2, 'token', 400),  # non-existing user
    (GroupUsers(users=['4']), 2, 'user_2_token', 403),  # not a creator
    (GroupUsers(users=['4']), 393, 'token', 404),  # non-existing group
])
async def test_delete_users_from_group_error(ac: AsyncClient, users, group_id, token, code):
    ac.headers['Authorization'] = f"Bearer {ac.headers.get(token)}"
    res = await ac.patch(f'/api/group/delete-from-group/{group_id}', json=users.dict())
    assert res.status_code == code
