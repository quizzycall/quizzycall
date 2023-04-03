from fastapi import APIRouter, Depends, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from db.user import login_user, create_user, validate_email_token
from db.settings import get_session
from validation import registration
from security.email import send_email
from security.config import testing

user_api = APIRouter()


@user_api.post("/registration-user")
async def registration_user(req: Request, back_tasks: BackgroundTasks, user: registration.RegistrationUser,
                            session: AsyncSession = Depends(get_session), is_testing=Depends(testing)):
    token = await create_user(user, session)
    res = {'access_token': token, 'token_type': 'bearer'}
    if not is_testing:
        mail = await send_email(dict(user)['email'], req.url_for('email_validation', token=res['access_token']))
        back_tasks.add_task(mail.get('fm').send_message, mail.get('message'))
    return res


@user_api.post("/login-user")
async def login_usr(user: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session),
                    is_testing=Depends(testing)):
    return {'access_token': await login_user(user, session, is_testing), 'token_type': 'bearer'}


@user_api.get('/email-validation/{token}')
async def email_validation(token: str, session: AsyncSession = Depends(get_session)):
    if await validate_email_token(token, session):
        return {'msg': 'Success email validation'}
