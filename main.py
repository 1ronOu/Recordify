from fastapi import FastAPI, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from typing import Annotated

from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

import models
from database import SessionLocal, engine
from targefy_app.routers import users, admin, targets, test, logout, register, records, error
from targefy_app.authenticaton import auth
import schemas
from targefy_app.authenticaton.validation import get_current_user
from targefy_app.authenticaton.utility import SECRET_KEY

app = FastAPI()
app.mount("/static", StaticFiles(directory="targefy_app/static"), name="static")
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(targets.router)
app.include_router(test.router)
app.include_router(logout.router)
app.include_router(register.router)
app.include_router(records.router)
app.include_router(error.router)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="targefy_app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/')
def root():
    return RedirectResponse(url='/records/?sort_by=date_added&order=asc', status_code=status.HTTP_302_FOUND)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(url='/auth/login', status_code=status.HTTP_302_FOUND)
    if exc.status_code == status.HTTP_417_EXPECTATION_FAILED:
        return RedirectResponse(url='/auth/refresh', status_code=status.HTTP_302_FOUND)
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        return RedirectResponse(url='/error/404', status_code=status.HTTP_302_FOUND)
    if exc.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        return RedirectResponse(url='/error/405', status_code=status.HTTP_302_FOUND)
    return await request.app.default_exception_handler(request, exc)
