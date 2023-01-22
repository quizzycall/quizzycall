from sqlmodel import select
from db.models.quiz import Quiz, Question, Answer, TimeOut 
from validation.quiz import AnswerOption, Question as QuestionW, Quiz as QuizW, TimeOut as TimeOutW
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


def create_quiz(quiz: QuestionW):
    print(quiz)
    quiz = dict(quiz)
    print(quiz)
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
    session.add(quiz_db)
    session.commit()
    session.refresh(quiz_db)
    print(dict(quiz_db))
    return dict(quiz_db)


def get_quiz_by_id(id: int):
    return session.exec(select(Quiz).where(Quiz.id == id)).first()


def get_question_by_id(id: int):
    return session.exec(select(Question).where(Question.id == id)).first()


def get_answer_by_id(id: int):
    return session.exec(select(Answer).where(Answer.id == id)).first()


def query_to_dict(query):
    res = {}
    for k, v in query:
        res[k] = v
    del res['_sa_instance_state']
    return res


def prepare_question(id: int):
    question = query_to_dict(get_question_by_id(id))
    question['answers'] = []
    for a in question['answers_id']:
        answer = query_to_dict(get_answer_by_id(a))
        if question.get('right_answer_id') and a == question['right_answer_id']:
            del question['right_answer_id']
            question['right_answer'] = answer
        question['answers'].append(answer)
    del question['answers_id']
    return question


def answers_for_front(question: dict):
    answers = {}
    num_of_answer = 1
    for a in question['answers']:
        answers[num_of_answer] = a
        num_of_answer += 1
    return answers


def results_of_question(data: list):
    res = {}
    for i in data:
        if not res.get(i['answer']['title']):
            res[i['answer']['title']] = 1
        else:
            res[i['answer']['title']] += 1
    return res


def start_quiz(id: int):
    quiz = get_quiz_by_id(id)
    quiz.start = True
    session.add(quiz)
    session.commit()
    session.refresh(quiz)
