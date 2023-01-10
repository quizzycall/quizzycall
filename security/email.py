from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from security.config import Config as cfg
from pydantic import EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME=cfg.MAIL_USERNAME,
    MAIL_PASSWORD=cfg.MAIL_PASSWORD,
    MAIL_FROM="quizzycall@email.com",
    MAIL_PORT=cfg.MAIL_PORT,
    MAIL_SERVER=cfg.MAIL_SERVER,
    MAIL_FROM_NAME="Quizzycall",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


async def send_email(email: EmailStr, url: str):
    html = f"""<a href={url}>Подтвердите почту</a>"""
    message = MessageSchema(
        subject="[Quizzycall] Подтверждение почты",
        recipients=[email],
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)
    return {'fm': fm, 'message': message}


async def send_change_password_email(email: EmailStr, url: str, back_tasks: BackgroundTasks):
    html = f"""<a href={url}>Подтвердите изменение пароля</a>"""
    message = MessageSchema(
        subject="[Quizzycall] Подтверждение изменения пароля",
        recipients=[email],
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)
    back_tasks.add_task(fm.send_message, message)
    return {'msg': 'Password change email was sent'}


async def send_email_changing(new_email: EmailStr, url: str, back_tasks: BackgroundTasks):
    html = f"""<a href={url}>Подтвердите изменение почты</a>"""
    message = MessageSchema(
        subject="[Quizzycall] Подтверждение изменения почты",
        recipients=[new_email],
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)
    back_tasks.add_task(fm.send_message, message)
    return {'msg': 'Email change was sent'}
