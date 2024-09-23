from fastapi import Depends, APIRouter, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse
from starlette.requests import Request

from targefy_app.authenticaton import helpers
import schemas
from targefy_app.authenticaton.validation import validate_auth_user, get_current_user_for_refresh
from targefy_app.authenticaton.dependencies import http_bearer, get_db

templates = Jinja2Templates(directory="targefy_app/templates")

router = APIRouter(prefix='/auth',
                   tags=['auth'],
                   dependencies=[Depends(http_bearer)],
                   )


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    return templates.TemplateResponse("login.html", {"request": request,
                                                     'error': error,
                                                     'current_url': request.url.path})


@router.post('/login', response_model=TokenInfo)
async def login_for_access_token(username=Form(...),
                                 password=Form(...),
                                 db: Session = Depends(get_db),
                                 ):
    user = validate_auth_user(db=db, username=username, password=password)

    if not user:
        return RedirectResponse(url="/auth/login?error=Invalid username or password",
                                status_code=status.HTTP_303_SEE_OTHER,
                                )

    access_token = helpers.create_access_token(user)
    refresh_token = helpers.create_refresh_token(user)

    response = RedirectResponse(url="/records/?sort_by=date_added&order=asc", status_code=303)

    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True)
    return response


@router.get('/refresh/', response_model=TokenInfo, response_model_exclude_none=True)
async def login_for_refresh_token(user: schemas.User = Depends(get_current_user_for_refresh)):
    access_token = helpers.create_access_token(user)
    response = RedirectResponse(url="/records/?sort_by=date_added&order=asc", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True)
    return response
