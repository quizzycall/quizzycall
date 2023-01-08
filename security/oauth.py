from fastapi import Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordBearer
from security.jwt import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/user/login_user', auto_error=False)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401)
    login = verify_token(token)
    return login


async def check_if_logged_in(token: str = Depends(oauth2_scheme)):
    if token:
        raise HTTPException(status_code=400, detail="You're already logged in")
