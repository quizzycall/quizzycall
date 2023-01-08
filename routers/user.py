from fastapi import APIRouter, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from db.user import LoginUser, CreateUser
from validation import login, registration
from security.oauth import check_if_logged_in

user_api = APIRouter()


@user_api.post("/registration_user")
async def registration_user(user: registration.RegistrationUser, check=Depends(check_if_logged_in)):
    return {'access_token': CreateUser(user), 'token_type': 'bearer'}

@user_api.post("/login_user")
async def login_user(user: OAuth2PasswordRequestForm = Depends(), check=Depends(check_if_logged_in)):
    return {'access_token': LoginUser(user), 'token_type': 'bearer'}
