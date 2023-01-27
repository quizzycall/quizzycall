from sqlmodel import select
from fastapi import HTTPException
from typing import Optional
from db.models.quiz import Quiz, Question, Answer, TimeOut
from .group import get_group_by_id
from validation.quiz import AnswerOption, Question as QuestionW, Quiz as QuizW, TimeOut as TimeOutW
from .user import get_user_data
from .settings import session


def create_timeout(timeout: TimeOutW):
    timeout = dict(timeout)
    timeout_db = TimeOut(hours=timeout["hours"], minutes=timeout["minutes"], seconds=timeout["seconds"])
    session.add(timeout_db)
    session.commit()
    return timeout_db.id


def create_answer(answer: AnswerOption):
    answer = dict(answer)
    answer_db = Answer(title=answer["title"])
    session.add(answer_db)
    session.commit()
    return answer_db.id


def create_question(question: QuestionW):
    question = dict(question)
    right_answer_id = 0
    list_answers_ids = []
    for answer in question["answer_options"]:
        answer = dict(answer)
        if answer["is_right"]:
            right_answer_db = create_answer(answer)
            right_answer_id = right_answer_db
            list_answers_ids.append(right_answer_id)
        else:
            answer_db = create_answer(answer)
            list_answers_ids.append(answer_db)
    question_db = Question(title=question["title"],
                           answers_id=list_answers_ids,
                           right_answer_id=right_answer_id,
                           amount_points=question["amount_points"])
    session.add(question_db)
    session.commit()
    return question_db.id


def create_quiz(quiz: QuestionW, group_id: Optional[int] = None):
    quiz = dict(quiz)
    questions_id = []
    for question in quiz["questions"]:
        question_db = create_question(question)
        questions_id.append(question_db)
    quiz_db = Quiz(creator_id=quiz["creator_id"],
                   title=quiz["title"],
                   max_points=quiz["max_points"],
                   timeout_id=create_timeout(quiz["timeout"]),
                   questions_id=questions_id,
                   start=quiz["start"],
                   amount_users=quiz["amount_users"])
    if group_id:
        quiz_db.group_id = group_id
    session.add(quiz_db)
    session.commit()
    session.refresh(quiz_db)
    return dict(quiz_db)


def get_quiz_by_id(quiz_id: int):
    return session.exec(select(Quiz).where(Quiz.id == quiz_id)).first()


def get_question_by_id(question_id: int):
    return session.exec(select(Question).where(Question.id == question_id)).first()


def get_answer_by_id(answer_id: int):
    return session.exec(select(Answer).where(Answer.id == answer_id)).first()


def get_timeout_by_id(timeout_id: int):
    return session.exec(select(TimeOut).where(TimeOut.id == timeout_id)).first()


def change_group_id(group_id: int, quiz_id: int, login: str):
    creator_id = get_user_data(login).id
    quiz = get_quiz_by_id(quiz_id)
    if quiz and quiz.creator_id == creator_id and get_group_by_id(group_id):
        quiz = get_quiz_by_id(quiz_id)
        quiz.group_id = group_id
        session.commit()
        return True
    raise HTTPException(status_code=400, detail="No such quiz, or group, or you're not a creator of this quiz")


def query_to_dict(query):
    res = {}
    for k, v in query:
        res[k] = v
    del res['_sa_instance_state']
    return res


def prepare_question(question_id: int):
    question = query_to_dict(get_question_by_id(question_id))
    question['_answers'] = []
    for a in question['answers_id']:
        answer = query_to_dict(get_answer_by_id(a))
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


def sum_points(data: dict):
    for name, points in data.items():
        user = get_user_data(name)
        user.points += points
        session.add(user)
    session.commit()


def start_quiz(quiz_id: int):
    quiz = get_quiz_by_id(quiz_id)
    quiz.start = True
    session.add(quiz)
    session.commit()
    session.refresh(quiz)
