from fastapi import APIRouter, Depends, BackgroundTasks, Request
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from db.user import login_user, create_user, validate_email_token
from validation import registration
from security.oauth import check_if_logged_in
from security.email import send_email

user_api = APIRouter()


@user_api.post("/registration_user")
async def registration_user(req: Request, back_tasks: BackgroundTasks, user: registration.RegistrationUser, check=Depends(check_if_logged_in)):
    res = {'access_token': create_user(user), 'token_type': 'bearer'}
    mail = await send_email(dict(user)['email'], req.url_for('email_validation') + f"?token={res['access_token']}")
    back_tasks.add_task(mail.get('fm').send_message, mail.get('message'))
    return res
    # return {'access_token': create_user(user), 'token_type': 'bearer'}


@user_api.post("/login_user")
async def login_usr(user: OAuth2PasswordRequestForm = Depends(), check=Depends(check_if_logged_in)):
    return {'access_token': login_user(user), 'token_type': 'bearer'}


# @user_api.post('/check_mail')
# async def check_mail(req: Request, mail: str, token: str, back_tasks: BackgroundTasks):
#     mail = await send_email(mail, req.url_for('email_validation')+f'?token={token}')
#     back_tasks.add_task(mail.get('fm').send_message, mail.get('message'))


@user_api.get('/email-validation')
async def email_validation(token: str):
    if validate_email_token(token):
        return {'msg': 'Success email validation'}
