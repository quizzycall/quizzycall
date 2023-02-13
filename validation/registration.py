from pydantic import BaseModel, EmailStr


class RegistrationUser(BaseModel):
    email: EmailStr
    nickname: str 
    password: str
    phone: str = None
