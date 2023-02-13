# user.py
# ----------

## /registration-user и /login-user 
### здесь регистрация/авторизация. можешь если че здесь посмотреть как сделать: https://github.com/Buuntu/fastapi-react/tree/master/%7B%7Bcookiecutter.project_slug%7D%7D/frontend/src/views

## /email-validation
### это для того чтоб юзер для подтверждения почты перешел сюда по ссылке в письме.

# ----------
# edit_user.py
# ----------

## /change-password-with-old-password/новый пароль/старый пароль
### меняет введенный старый пароль на новый.

## /change-password-with-email/новый пароль
### меняет пароль, отправляя подтверждение на емейл.

## /change-password-with-email-validation/токен
### сюда юзер переходит по ссылке из подтверждения о смене пароля.

## /change-email/новый емейл
### меняет емейл, отправляя подтверждение на новый емейл

## /change-email-validation/токен
### сюда юзер переходит по ссылке из подтверждения о смене почты.

## /change-nickname/новый ник
### меняет ник

## /change-phone-number/новый номер
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

# ----------
# quiz.py
# ----------

## /create_quiz
### создает квиз

## /edit-quiz/{quiz_id}
### редактирование квиза

## /get-quiz/{quiz_id}
### получение квиза по айди

## /play-quiz/{quiz_id}
### старт квиза. возвращает пин-код по которому игроки и создатель должны присоединиться.

## /client/session-quiz/{pin} и /client/session-quiz-creator/{pin}
### это тестовые html странички, можно не трогать

## /session-quiz/{pin} и /session-quiz-creator/{pin}
### сокеты для юзера и создателя

