import decimal
from datetime import datetime
from typing import Annotated, List

from fastapi import Depends, APIRouter, HTTPException, status, Form
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
    prefix='/target',
    tags=['targets'],
    dependencies=[Depends(http_bearer)]
)


@router.get('/read_all_targets/{record_id}', response_class=HTMLResponse)
async def read_all_targets(request: Request,
                           current_user: Annotated[schemas.User, Depends(get_current_user)],
                           record_id: int,
                           db: Session = Depends(get_db),
                           ):
    msg = request.session.pop("update_msg", None)

    targets_model = crud.read_all_targets(db=db, user=current_user, record_id=record_id)[::-1]
    record_name = crud.read_record_name(db=db, user=current_user, record_id=record_id)
    record_unit = crud.read_record_unit(db=db, user=current_user, record_id=record_id)

    total_value = 0
    number_of_targets = 0  
    max_value = 0

    for target in targets_model:
        total_value += target.value
        if target.value > max_value:
            max_value = target.value
        if target.value > 0:
            number_of_targets += 1
        if number_of_targets == 0:
            number_of_targets = 1

    average = round(total_value / number_of_targets, 2)

    return templates.TemplateResponse("targets.html", {
        "request": request,
        "targets_model": targets_model,
        'total_value': total_value,
        'number_of_targets': number_of_targets,
        'max_value': max_value,
        'average': average,
        'record_id': record_id,
        'record_name': record_name,
        'record_unit': record_unit,
        'msg': msg,
    })


@router.post('/create_target', response_class=HTMLResponse)
async def create_target(request: Request,
                        current_user: Annotated[schemas.User, Depends(get_current_user)],
                        record_id=Form(...),
                        value=Form(...),
                        db: Session = Depends(get_db),
                        ):
    crud.create_target(db=db, value=value, user=current_user, record_id=record_id)
    request.session['update_msg'] = 'Target value updated'
    return RedirectResponse(url=f"/target/read_all_targets/{record_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.get('/update_target/{record_id}/{target_id}', response_class=HTMLResponse)
async def update_target_page(request: Request,
                             current_user: Annotated[schemas.User, Depends(get_current_user)],
                             target_id: int,
                             record_id: int,
                             db: Session = Depends(get_db)):
    target_model = crud.get_target_model(db=db, user=current_user, target_id=target_id, record_id=record_id)
    return templates.TemplateResponse("target_edit.html", {"request": request,
                                                           'target_id': target_id,
                                                           'record_id': record_id,
                                                           'added_at': target_model.added_at,
                                                           })


@router.post('/update_target/{record_id}/{target_id}', response_class=HTMLResponse)
async def update_target(request: Request,
                        current_user: Annotated[schemas.User, Depends(get_current_user)],
                        target_id: int,
                        record_id: int,
                        value_for_update=Form(...),
                        db: Session = Depends(get_db),
                        ):
    target_model = crud.update_target(db=db, user=current_user, target_id=target_id, record_id=record_id)
    if target_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Target not found or you have no rights to read it')

    target_model.value = value_for_update
    request.session['update_msg'] = 'Target value updated'
    db.add(target_model)
    db.commit()
    return RedirectResponse(url=f"/target/read_all_targets/{record_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post('/delete_target/{target_id}', response_class=HTMLResponse)
async def delete_target(current_user: Annotated[schemas.User, Depends(get_current_user)],
                        target_id: int,
                        db: Session = Depends(get_db),
                        ):
    target_model = crud.delete_target(db=db, user=current_user, target_id=target_id)
    if target_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Target not found or you have no rights to read it')
    db.delete(target_model)
    db.commit()
    return RedirectResponse(url="/target/read_all_targets", status_code=status.HTTP_303_SEE_OTHER)
