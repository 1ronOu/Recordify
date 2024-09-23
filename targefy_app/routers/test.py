from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.requests import Request
from targefy_app.authenticaton.validation import get_current_user
import schemas
import crud
from targefy_app.authenticaton.dependencies import get_db


router = APIRouter()
templates = Jinja2Templates(directory="targefy_app/templates")


@router.get("/read_target/{target_id}", response_class=HTMLResponse)
async def read_root(target_id: int,
                    request: Request,
                    current_user: Annotated[schemas.User, Depends(get_current_user)],
                    db: Session = Depends(get_db),
                    ):
    target = crud.read_single_target(db=db, user=current_user, target_id=target_id)
    print(f"Retrieved target: {target}")
    return templates.TemplateResponse("index.html",
                                      {"request": request,
                                       "title": "My Targets",
                                       "heading": "Your Targets",
                                       "target": target},
                                      )
