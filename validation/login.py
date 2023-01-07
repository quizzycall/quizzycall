from pydantic import BaseModel, EmailStr

class LoginUser(BaseModel):
    login: EmailStr
    password: str