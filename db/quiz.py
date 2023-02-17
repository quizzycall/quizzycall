import random
from typing import List
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from db.models.quiz import Quiz, Question, Answer, TimeOut
from .group import get_group_by_id
from validation.quiz import AnswerOption, Question as QuestionVal, Quiz as QuizVal, TimeOut as TimeOutW, QuizEdit
from .user import get_user_data


async def create_timeout(timeout: TimeOutW, session: AsyncSession):
    timeout = dict(timeout)
    timeout_db = TimeOut(hours=timeout["hours"], minutes=timeout["minutes"], seconds=timeout["seconds"])
    session.add(timeout_db)
    await session.flush()
    return timeout_db.id


async def create_answer(answer: AnswerOption, session: AsyncSession):
    answer = dict(answer)
    answer_db = Answer(title=answer["title"])
    session.add(answer_db)
    await session.flush()
    return answer_db.id


async def create_question(question: QuestionVal, session: AsyncSession):
    question = dict(question)
    right_answer_id = 0
    list_answers_ids = []
    for answer in question["answers"]:
        answer = dict(answer)
        if answer["is_right"]:
            right_answer_db = await create_answer(answer, session)
            right_answer_id = right_answer_db
            list_answers_ids.append(right_answer_id)
        else:
            answer_db = await create_answer(answer, session)
            list_answers_ids.append(answer_db)
    question_db = Question(title=question["title"],
                           answers_id=list_answers_ids,
                           right_answer_id=right_answer_id,
                           amount_points=question["amount_points"])
    session.add(question_db)
    await session.flush()
    return question_db.id


async def create_quiz(quiz: QuizVal, login: str, session: AsyncSession):
    _u = await get_user_data(login, session)
    quiz = dict(quiz)
    creator_id = _u.id
    if quiz['group_id']:
        group = await get_group_by_id(quiz['group_id'], session)
        if group.creator_id != creator_id:
            raise HTTPException(status_code=403, detail="You're not a creator of this group")
    quiz["creator_id"] = creator_id
    questions_id = []
    for question in quiz["questions"]:
        question_db = await create_question(question, session)
        questions_id.append(question_db)
    quiz_db = Quiz(creator_id=quiz["creator_id"],
                   title=quiz["title"],
                   max_points=quiz["max_points"],
                   timeout_id=await create_timeout(quiz["timeout"], session),
                   questions_id=questions_id,
                   amount_users=quiz["amount_users"],
                   group_id=quiz['group_id'])
    session.add(quiz_db)
    await session.commit()
    await session.refresh(quiz_db)
    return dict(quiz_db)


async def get_quiz_by_id(quiz_id: int, session: AsyncSession):
    r = await session.execute(select(Quiz).where(Quiz.id == quiz_id))
    r = r.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail='No such quiz')
    return r


async def get_quiz_by_id_dict(quiz_id: int, session: AsyncSession):
    r = await session.execute(select(Quiz).where(Quiz.id == quiz_id))
    r = r.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail='No such quiz')
    res = r.dict().copy()
    del res['timeout_id']
    res['timeout'] = await get_timeout_by_id(r.timeout_id, session)
    res['questions'] = await get_questions_and_answers_by_id(res['questions_id'], session)
    del res['questions_id']
    return res


async def get_question_by_id(question_id: int, session: AsyncSession):
    r = await session.execute(select(Question).where(Question.id == question_id))
    return r.scalar_one_or_none()


async def get_answer_by_id(answer_id: int, session: AsyncSession):
    r = await session.execute(select(Answer).where(Answer.id == answer_id))
    return r.scalar_one_or_none()


async def get_questions_and_answers_by_id(questions_id: list, session: AsyncSession):
    result = []
    for question_id in questions_id:
        question = await session.execute(select(Question).where(Question.id == question_id))
        question = question.scalar_one_or_none().dict().copy()
        question['answers'] = []
        for answer_id in question['answers_id']:
            answer = await get_answer_by_id(answer_id, session)
            question['answers'].append(answer.dict().copy())
        del question['answers_id']
        result.append(question)
    return result


async def get_timeout_by_id(timeout_id: int, session: AsyncSession):
    r = await session.execute(select(TimeOut).where(TimeOut.id == timeout_id))
    return r.scalar_one_or_none()


def query_to_dict(query):
    res = {}
    for k, v in query:
        res[k] = v
    del res['_sa_instance_state']
    return res


async def prepare_question(question_id: int, session: AsyncSession):
    question = query_to_dict(await get_question_by_id(question_id, session))
    question['_answers'] = []
    for a in question['answers_id']:
        answer = query_to_dict(await get_answer_by_id(a, session))
        if question.get('right_answer_id') and a == question['right_answer_id']:
            del question['right_answer_id']
            question['right_answer'] = answer
        question['_answers'].append(answer)
    del question['answers_id']
    return question


def answers_for_front(question: dict):
    answers = {}
    num_of_answer = 1
    for a in question['_answers']:
        answers[num_of_answer] = a
        num_of_answer += 1
    return answers


def results_of_question(data: dict):
    res = {}
    for k, _ in data.items():
        res[k] = len(data[k])
    return res


async def sum_points(data: dict, session: AsyncSession):
    for name, points in data.items():
        user = await get_user_data(name, session)
        user.points += points
        session.add(user)
    await session.commit()


async def get_pin(rooms: dict):
    while True:
        pin = random.randint(100000, 999999)
        if pin not in rooms:
            return pin


async def start_quiz(quiz_id: int, session: AsyncSession):
    quiz = await get_quiz_by_id(quiz_id, session)
    quiz.start = True
    session.add(quiz)
    await session.commit()
    await session.refresh(quiz)


async def checking_to_change_group_id(group_id: int, creator_id: int, quiz: Quiz, session: AsyncSession):
    if quiz.creator_id == creator_id and await get_group_by_id(group_id, session):
        quiz.group_id = group_id
        return True
    raise HTTPException(status_code=403, detail="You're not a creator of this quiz")


async def editing_answers(new_answers: List[dict], session: AsyncSession):
    is_right = None
    for new_answer in new_answers:
        answer = await get_answer_by_id(new_answer['id'], session)
        for k, v in new_answer.items():
            if k == 'is_right':
                if v:
                    is_right = new_answer['id']
            else:
                setattr(answer, k, v)

    return is_right


async def editing_timeout(timeout_id: int, new_timeout: dict, session: AsyncSession):
    timeout = await get_timeout_by_id(timeout_id, session)
    for k1, v1 in new_timeout.items():
        setattr(timeout, k1, v1)


async def editing_questions(new_questions: List[dict], session: AsyncSession):
    for new_question in new_questions:
        question = await get_question_by_id(new_question['id'], session)
        for k, v in new_question.items():
            if k == 'answers':
                setattr(question, 'right_answer_id', await editing_answers(v, session))
            else:
                setattr(question, k, v)


async def edit_quiz(quiz_id: int, quiz_edit: QuizEdit, login: str, session: AsyncSession):
    user = await get_user_data(login, session)
    quiz_edit = quiz_edit.dict(exclude_unset=True)
    quiz = await get_quiz_by_id(quiz_id, session)
    group = await get_group_by_id(quiz_edit['group_id'], session)
    if user.id == quiz.creator_id or user.id in group.participants_id:
        for k, v in quiz_edit.items():
            if k == 'group_id':
                if await checking_to_change_group_id(v, group.creator_id, quiz, session):
                    setattr(quiz, k, v)
            elif k == 'timeout':
                await editing_timeout(quiz.timeout_id, v, session)
            elif k == 'questions':
                await editing_questions(v, session)
            else:
                setattr(quiz, k, v)
        await session.commit()
        await session.refresh(quiz)
        return quiz
    raise HTTPException(status_code=403, detail="You can't edit this quiz")

