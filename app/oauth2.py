import os

from jose import JWTError, jwt
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from datetime import datetime, timedelta

from app import schemas, database, models
from .config import settings

# tokenURLはログインのためのエンドポイントを渡す
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=int(settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def verify_access_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

        id: int = payload.get("user_id")
        print(id)

        if id is None:
            raise credential_exception

        token_data = schemas.TokenData(id=id)

    # expiredな場合、ここに入る
    except JWTError as e:
        raise credential_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)) -> schemas.UserResponse:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials.",
                                          headers={"WWW-Authenticate": "Bearer"})
    token_data = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(token_data.id == models.User.id).first()

    if not user:
        raise credentials_exception

    return schemas.UserResponse.from_orm(user)
