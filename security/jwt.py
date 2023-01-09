from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from security.config import Config as cfg


def create_token(data: dict):
    to_encode = data.copy()
    exp = datetime.now() + timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': exp})
    encoded_jwt = jwt.encode(to_encode, cfg.SECRET_KEY, algorithm=cfg.ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        decoded_token = jwt.decode(token, cfg.SECRET_KEY, algorithms=[cfg.ALGORITHM])
        login = decoded_token.get('login')
        if login:
            return login
        raise HTTPException(status_code=400, detail='Invalid token')
    except JWTError:
        raise HTTPException(status_code=400, detail='Invalid token')


def decode_token(token: str):
    try:
        return jwt.decode(token, cfg.SECRET_KEY, algorithms=[cfg.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=400, detail='Invalid token')
