from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, Form,  Request, Response
from fastapi.responses import RedirectResponse
from jwt.exceptions import InvalidTokenError
from starlette import status
from targefy_app.authenticaton.helpers import TOKEN_TYPE_FIELD, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from targefy_app.authenticaton import utility
from sqlalchemy.orm import Session
from targefy_app.authenticaton.dependencies import oauth2_scheme, get_db
from targefy_app.authenticaton.helpers import create_access_token
import schemas
import models


def validate_auth_user(db: Session,
                       username: str = Form(...),
                       password: str = Form(...),
                       ):
    unauthed_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail='Invalid username or password')
    user_model = db.query(models.User).filter(models.User.username == username).first()
    if user_model is None:
        return False

    if not utility.verify_password(plain_password=password, hashed_password=user_model.hashed_password):
        return False

    return user_model


async def get_current_user(response: Response,
                           request: Request,
                           db: Session = Depends(get_db),
                           ):
    access_token = request.cookies.get('access_token')
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(access_token, utility.SECRET_KEY, algorithms=[utility.ALGORITHM])
        username: str = payload.get("sub")
        token_type = payload.get(TOKEN_TYPE_FIELD)
        if token_type != ACCESS_TOKEN_TYPE:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=f'Invalid token type {token_type!r} expected {ACCESS_TOKEN_TYPE!r}',
                                )
        if username is None:
            raise credentials_exception
        user = db.query(models.User).filter(models.User.username == username).first()
        if user is None:
            raise credentials_exception
        if not user.is_active:
            raise HTTPException(status_code=400, detail='Inactive User')
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail='token expired')
    except jwt.InvalidSignatureError:
        raise credentials_exception


async def get_current_user_for_refresh(request: Request,
                                       response: Response,
                                       db: Session = Depends(get_db),
                                       ):
    refresh_token = request.cookies.get('refresh_token')
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not refresh_token:
        raise credentials_exception

    try:
        payload = jwt.decode(refresh_token, utility.SECRET_KEY, algorithms=[utility.ALGORITHM])
        username: str = payload.get("sub")
        token_type = payload.get(TOKEN_TYPE_FIELD)
        if token_type != REFRESH_TOKEN_TYPE:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=f'Invalid token type {token_type!r} expected {REFRESH_TOKEN_TYPE!r}',
                                )
        if username is None:
            raise credentials_exception
    except jwt.InvalidSignatureError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail='Inactive User')

    return user
