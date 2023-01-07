from fastapi import APIRouter
from db.user import LoginUser, CreateUser
from validation import login, registration

user_api = APIRouter()

@user_api.post("/registration_user")
async def registration_user(user: registration.RegistrationUser):
    return CreateUser(user)

@user_api.post("/login_user")
async def login_user(user: login.LoginUser):
    return LoginUser(user)