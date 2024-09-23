from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import HTTPBearer

import targefy_app.authenticaton.validation
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import schemas
import crud
from targefy_app.authenticaton.validation import get_current_user

http_bearer = HTTPBearer(auto_error=False)
router = APIRouter(
    prefix='/users',
    tags=['users'],
    dependencies=[Depends(http_bearer)]
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/read_user/me', response_model=schemas.UserBase)
async def read_user_me(current_user: Annotated[schemas.User, Depends(get_current_user)],):
    return current_user
