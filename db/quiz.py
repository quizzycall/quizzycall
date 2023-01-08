from sqlmodel import SQLModel, Session, create_engine, select
from db.models.quiz import Quiz, Question, Answer, TimeOut 
from validation.quiz import AnswerOption, Question as QuestionW, Quiz as QuizW, TimeOut as TimeOutW
import os

engine = create_engine(os.getenv("PSQL_URL"))

SQLModel.metadata.create_all(engine)

session = Session(engine)

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
    question_db = Question(title=question["title"], answers_id=list_answers_ids, right_answer_id=right_answer_id, amount_points=question["amount_points"])
    session.add(question_db)
    session.commit()
    return question_db.id

def create_quiz(quiz: QuestionW):
    quiz = dict(quiz)
    questions_id = []
    for question in quiz["questions"]:
        question_db = create_question(question)
        questions_id.append(question_db)
    quiz_db = Quiz(creator_id=1, title=quiz["title"], max_points=quiz["max_points"], timeout_id=create_timeout(quiz["timeout"]), questions_id=questions_id, start=quiz["start"], amount_users=quiz["amount_users"])
    session.add(quiz_db)
    session.commit()
    return dict(quiz_db)