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
    prefix='/records',
    tags=['records'],
    dependencies=[Depends(http_bearer)]
)


@router.get('/')
async def read_all_records(request: Request,
                           current_user: Annotated[schemas.User, Depends(get_current_user)],
                           sort_by: str,
                           order: str,
                           db: Session = Depends(get_db),
                           ):
    msg = request.session.pop("msg", None)
    print(sort_by, order)
    records_model = crud.read_all_records(db=db, user=current_user, sort_by=sort_by, order=order)
    return templates.TemplateResponse("records_page.html", {
        'request': request,
        "records_model": records_model,
        'msg': msg,
        'sort_by': sort_by,
        'order': order,
    })


@router.get('/settings/{record_id}')
async def record_settings(request: Request,
                          current_user: Annotated[schemas.User, Depends(get_current_user)],
                          record_id: int,
                          db: Session = Depends(get_db)):
    record_model = crud.get_record_model(user=current_user, record_id=record_id, db=db)
    return templates.TemplateResponse('record_settings.html', {
        'request': request,
        'record_id': record_id,
        'record_model': record_model,
    })


@router.post('/change_record_name/{record_id}')
async def change_record_name(request: Request,
                             record_id: int,
                             current_user: Annotated[schemas.User, Depends(get_current_user)],
                             db: Session = Depends(get_db),
                             record_name=Form(...),
                             ):
    record_model = crud.get_record_model(record_id=record_id, user=current_user, db=db)

    record_model.record_name = record_name
    db.add(record_model)
    db.commit()

    request.session["msg"] = "Record name successfully changed"

    return RedirectResponse(url='/records/?sort_by=date_added&order=asc', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/change_record_unit/{record_id}')
async def change_record_unit(request: Request,
                             record_id: int,
                             current_user: Annotated[schemas.User, Depends(get_current_user)],
                             db: Session = Depends(get_db),
                             new_record_unit=Form(...),
                             ):
    record_model = crud.get_record_model(record_id=record_id, user=current_user, db=db)

    record_model.unit = new_record_unit
    db.add(record_model)
    db.commit()

    request.session['msg'] = 'Record unit of measurement successfully changed'

    return RedirectResponse(url='/records/?sort_by=date_added&order=asc', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/create_record')
async def create_new_record(request: Request,
                            current_user: Annotated[schemas.User, Depends(get_current_user)],
                            ):
    return templates.TemplateResponse('create_record.html', {'request': request})


@router.post('/create_record')
async def create_new_record(request: Request,
                            current_user: Annotated[schemas.User, Depends(get_current_user)],
                            record_unit=Form(...),
                            record_name=Form(...),
                            db: Session = Depends(get_db)):
    crud.create_record(db=db, user=current_user, record_name=record_name, record_unit=record_unit)
    request.session['msg'] = 'Record successfully created'
    return RedirectResponse(url='/records/?sort_by=date_added&order=asc', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/delete_record/{record_id}')
async def delete_record(request: Request,
                        record_id: int,
                        current_user: Annotated[schemas.User, Depends(get_current_user)],
                        db: Session = Depends(get_db),
                        ):
    crud.delete_record_model(user=current_user, record_id=record_id, db=db)
    request.session['msg'] = 'Record successfully deleted'
    return RedirectResponse(url='/records/?sort_by=date_added&order=asc', status_code=status.HTTP_303_SEE_OTHER)
