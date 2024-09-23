import decimal
from typing import Annotated, List

from fastapi import Depends, APIRouter, HTTPException, status, Form
from sqlalchemy import desc
from starlette.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

import models
from database import engine
from sqlalchemy.orm import Session
import schemas
import crud
from targefy_app.authenticaton.validation import get_current_user
from targefy_app.authenticaton.dependencies import http_bearer, get_db

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="targefy_app/templates")

router = APIRouter(
    prefix='/error',
    tags=['error'],
    dependencies=[Depends(http_bearer)]
)


@router.get('/404')
async def error404(request: Request):
    status_code = 404
    status_desc = 'NOT FOUND'
    return templates.TemplateResponse('error.html', {'request': request,
                                                     'status_code': status_code,
                                                     'status_desc': status_desc,
                                                     })


@router.get('/405')
async def error405(request: Request):
    status_code = 405
    status_desc = 'METHOD NOT ALLOWED'
    return templates.TemplateResponse('error.html', {'request': request,
                                                     'status_code': status_code,
                                                     'status_desc': status_desc,
                                                     })
