from fastapi import APIRouter, Depends, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from db.user import login_user, create_user, validate_email_token
from db.settings import get_session
from validation import registration
from security.email import send_email

user_api = APIRouter()


@user_api.post("/registration_user")
async def registration_user(req: Request, back_tasks: BackgroundTasks, user: registration.RegistrationUser,
                            session: AsyncSession = Depends(get_session)):
    token = await create_user(user, session)
    res = {'access_token': token, 'token_type': 'bearer'}
    mail = await send_email(dict(user)['email'], req.url_for('email_validation') + f"?token={res['access_token']}")
    back_tasks.add_task(mail.get('fm').send_message, mail.get('message'))
    return res


@user_api.post("/login_user")
async def login_usr(user: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    return {'access_token': await login_user(user, session), 'token_type': 'bearer'}


@user_api.get('/email-validation')
async def email_validation(token: str, session: AsyncSession = Depends(get_session)):
    if await validate_email_token(token, session):
        return {'msg': 'Success email validation'}
