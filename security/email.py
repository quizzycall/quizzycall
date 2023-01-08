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
