import pytest
from httpx import AsyncClient
from db.quiz import get_quiz_by_id_dict, get_timeout_by_id, get_quiz_by_id
from sqlalchemy.ext.asyncio import AsyncSession
from validation.quiz import Quiz, QuizEdit, TimeOut, Question, AnswerOption, TimeOutEdit, QuestionEdit, AnswerOptionEdit


async def test_create_quiz(ac: AsyncClient):
    quiz_data = Quiz(
        group_id=2,
        title='quiz2',
        timeout=TimeOut(hours=0, minutes=1, seconds=0),
        questions=[
            Question(
                title='q1',
                amount_points=10,
                answers=[
                    AnswerOption(title='a1', is_right=True),
                    AnswerOption(title='a2', is_right=False)
                ]
            ),
            Question(
                title='q2',
                amount_points=10,
                answers=[
                    AnswerOption(title='a1', is_right=False),
                    AnswerOption(title='a2', is_right=True)
                ]
            )
        ],
        max_points=20,
        amount_users=2,
        start=False
    )
    res = await ac.post('/api/quiz/create-quiz', json=quiz_data.dict())
    assert res.status_code == 200
    ac.headers['Authorization'] = f"Bearer {ac.headers.get('user_2_token')}"
    quiz_data.group_id = 1
    await ac.post('/api/quiz/create-quiz', json=quiz_data.dict())


@pytest.mark.parametrize('quiz_data, token, code',
                         [
                             (Quiz(
                                 group_id=2,
                                 title='quiz2',
                                 timeout=TimeOut(hours=0, minutes=1, seconds=0),
                                 questions=[
                                     Question(
                                         title='q1',
                                         amount_points=10,
                                         answers=[
                                             AnswerOption(title='a1', is_right=True),
                                             AnswerOption(title='a2', is_right=False)
                                         ]
                                     ),
                                     Question(
                                         title='q2',
                                         amount_points=10,
                                         answers=[
                                             AnswerOption(title='a1', is_right=False),
                                             AnswerOption(title='a2', is_right=True)
                                         ]
                                     )
                                 ],
                                 max_points=20,
                                 amount_users=2,
                                 start=False
                             ), 'user_2_token', 403),  # not a creator
                             (Quiz(
                                 group_id=12323,  # non-existing group
                                 title='quiz2',
                                 timeout=TimeOut(hours=0, minutes=1, seconds=0),
                                 questions=[
                                     Question(
                                         title='q1',
                                         amount_points=10,
                                         answers=[
                                             AnswerOption(title='a1', is_right=True),
                                             AnswerOption(title='a2', is_right=False)
                                         ]
                                     ),
                                     Question(
                                         title='q2',
                                         amount_points=10,
                                         answers=[
                                             AnswerOption(title='a1', is_right=False),
                                             AnswerOption(title='a2', is_right=True)
                                         ]
                                     )
                                 ],
                                 max_points=20,
                                 amount_users=2,
                                 start=False
                             ), 'token', 404)
                         ])
async def test_create_quiz_error(ac: AsyncClient, quiz_data, token, code):
    ac.headers['Authorization'] = f"Bearer {ac.headers.get(token)}"
    res = await ac.post('/api/quiz/create-quiz', json=quiz_data.dict())
    assert res.status_code == code


async def test_get_quiz_url(ac: AsyncClient):
    res = await ac.get('/api/quiz/get-quiz/1')
    assert res.status_code == 200


async def test_get_quiz_url_error(ac: AsyncClient):
    res = await ac.get('/api/quiz/get-quiz/234')  # non-existing group
    assert res.status_code == 404


async def test_edit_quiz_url(ac: AsyncClient, session: AsyncSession):
    quiz_data = QuizEdit(
        group_id=2,
        title='quiz11',
        timeout=TimeOutEdit(hours=0, minutes=0, seconds=55),
        questions=[
            QuestionEdit(
                id=1,
                title='q1',
                amount_points=15,
                answers=[
                    AnswerOptionEdit(id=1, title='a1', is_right=False),
                    AnswerOptionEdit(id=2, title='a2', is_right=True)
                ]
            ),
            QuestionEdit(
                id=2,
                title='q2',
                amount_points=15,
                answers=[
                    AnswerOptionEdit(id=3, title='a1', is_right=True),
                    AnswerOptionEdit(id=4, title='a2', is_right=False)
                ]
            )
        ],
        max_points=30,
        amount_users=3
    )
    res = await ac.patch('/api/quiz/edit-quiz/1', json=quiz_data.dict())
    quiz = await get_quiz_by_id_dict(1, session)
    assert res.status_code == 200
    assert quiz['group_id'] == quiz_data.group_id
    assert quiz['title'] == quiz_data.title
    t = await get_timeout_by_id(quiz['timeout'].id, session)
    timeout = t.dict()
    del timeout['id']
    assert timeout == quiz_data.timeout
    quiz_data = quiz_data.dict()
    del quiz_data['questions'][0]['answers'][0]['is_right']
    del quiz_data['questions'][0]['answers'][1]['is_right']
    del quiz_data['questions'][1]['answers'][0]['is_right']
    del quiz_data['questions'][1]['answers'][1]['is_right']
    assert quiz_data['questions'][0]['title'] == quiz['questions'][0]['title']
    assert quiz_data['questions'][0]['amount_points'] == quiz['questions'][0]['amount_points']
    assert quiz_data['questions'][0]['answers'] == quiz['questions'][0]['answers']
    assert quiz_data['questions'][1]['title'] == quiz['questions'][1]['title']
    assert quiz_data['questions'][1]['amount_points'] == quiz['questions'][1]['amount_points']
    assert quiz_data['questions'][1]['answers'] == quiz['questions'][1]['answers']


async def test_edit_quiz_url_error(ac: AsyncClient, session: AsyncSession):
    quiz_data = QuizEdit(
        group_id=3,  # not a creator of group
        title='quiz11',
        timeout=TimeOutEdit(hours=0, minutes=0, seconds=55),
        questions=[
            QuestionEdit(
                id=1,
                title='q1',
                amount_points=15,
                answers=[
                    AnswerOptionEdit(id=1, title='a1', is_right=False),
                    AnswerOptionEdit(id=2, title='a2', is_right=True)
                ]
            ),
            QuestionEdit(
                id=2,
                title='q2',
                amount_points=15,
                answers=[
                    AnswerOptionEdit(id=3, title='a1', is_right=True),
                    AnswerOptionEdit(id=4, title='a2', is_right=False)
                ]
            )
        ],
        max_points=30,
        amount_users=3
    )
    res = await ac.patch('/api/quiz/edit-quiz/1', json=quiz_data.dict())
    assert res.status_code == 403


async def test_play_quiz(ac: AsyncClient):
    res = await ac.get('/api/quiz/play-quiz/1')
    assert res.status_code == 200


async def test_play_quiz_error(ac: AsyncClient):
    res = await ac.get('/api/quiz/play-quiz/2')  # not a creator
    assert res.status_code == 403
    res = await ac.get('/api/quiz/play-quiz/3')  # non-existing
    assert res.status_code == 404


