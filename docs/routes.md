# user.py
# ----------

## /registration_user и /login_user 
### здесь регистрация/авторизация. можешь если че здесь посмотреть как сделать: https://github.com/Buuntu/fastapi-react/tree/master/%7B%7Bcookiecutter.project_slug%7D%7D/frontend/src/views

## /email-validation
### это для того чтоб юзер для подтверждения почты перешел сюда по ссылке в письме.

# ----------
# edit_user.py
# ----------

## /change-password-with-old-password
### меняет введенный старый пароль на новый.

## /change-password-with-email
### меняет пароль, отправляя подтверждение на емейл.

## /change-password-with-email-validation
### сюда юзер переходит по ссылке из подтверждения о смене пароля.

## /change-email
### меняет емейл, отправляя подтверждение на новый емейл

## /change-email-validation
### сюда юзер переходит по ссылке из подтверждения о смене почты.

## /change-nickname
### меняет ник

## /change-phone-number
### меняет номер телефона

# ----------
# group.py
# ----------

## /create-group
### создает группу

## /get-group/{group_id}
### получет группу по её айди

## /add-to-group/{group_id}
### добавляет юзеров(по никнейму) в группу

## /delete-from-group/{group_id}
### удаляет юзеров(по никнейму) из группы

## /change-group-id-of-quiz/{group_id}/{quiz_id}
### меняет айди группы в квизе

# ----------
# quiz.py
# ----------

## /create_quiz
### создает квиз

## /edit-quiz/{quiz_id}
### редактирование квиза

## /get_quiz/{quiz_id}
### получение квиза по айди

## /play_quiz/{quiz_id}
### старт квиза. возвращает пин-код по которому игроки и создатель должны присоединиться.

## /client/session_quiz/{pin} и /client/session_quiz_creator/{pin}
### это тестовые html странички, можно не трогать

## /session_quiz/{pin} и /session_quiz_creator/{pin}
### сокеты для юзера и создателя

