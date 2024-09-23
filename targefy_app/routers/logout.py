from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from targefy_app.authenticaton.validation import get_current_user

router = APIRouter()


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return response
