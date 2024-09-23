from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException, Form
from starlette import status
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request
from starlette.templating import Jinja2Templates

import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import schemas
import crud
from targefy_app.authenticaton.validation import get_current_user
from targefy_app.authenticaton.dependencies import get_db

templates = Jinja2Templates(directory="targefy_app/templates")

models.Base.metadata.create_all(bind=engine)


router = APIRouter(
    prefix='/register',
    tags=['register'],
)


@router.get('/', response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post('/', response_class=HTMLResponse)
async def register(request: Request,
                   username=Form(...),
                   email=Form(...),
                   password=Form(...),
                   db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=email, username=username)
    if user:
        raise HTTPException(status_code=400, detail='Email or username already registered')
    crud.create_user(db=db, username=username, email=email, password=password)
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
