from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from security.oauth import get_current_user
from pydantic import EmailStr
from db.edit_user import change_password_with_old_password, send_change_password_with_email, \
    change_password_after_email, change_email, change_email_validation, change_nickname, change_phone
from db.settings import get_session
user_edit_api = APIRouter()


@user_edit_api.patch('/change-password-with-old-password')
async def change_pass_with_old_pass(new_pass: str, old_pass: str, login=Depends(get_current_user),
                                    session: AsyncSession = Depends(get_session)):
    return await change_password_with_old_password(new_pass, old_pass, login, session)


@user_edit_api.patch('/change-password-with-email')
async def change_pass_with_email(back_tasks: BackgroundTasks, req: Request, new_pass: str,
                                 login=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await send_change_password_with_email(new_pass, req.url_for('change_pass_with_email_validation'), login,
                                                 back_tasks, session)


@user_edit_api.patch('/change-password-with-email-validation')
async def change_pass_with_email_validation(token: str, session: AsyncSession = Depends(get_session)):
    return await change_password_after_email(token, session)


@user_edit_api.patch('/change-email')
async def change_user_email(new_email: EmailStr, back_tasks: BackgroundTasks, req: Request,
                            login=Depends(get_current_user)):
    await change_email(new_email, req.url_for('change_email_val'), login, back_tasks)


@user_edit_api.get('/change-email-validation')
async def change_email_val(token: str, session: AsyncSession = Depends(get_session)):
    return await change_email_validation(token, session)


@user_edit_api.patch('/change-nickname')
async def change_nick(new_nick: str, login=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await change_nickname(new_nick, login, session)


@user_edit_api.patch('/change-phone-number')
async def change_phone_num(new_phone_num: str, login=Depends(get_current_user),
                           session: AsyncSession = Depends(get_session)):
    return await change_phone(new_phone_num, login, session)
