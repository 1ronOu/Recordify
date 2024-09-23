from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException, status

import targefy_app.authenticaton.validation
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import schemas

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/get_all_users/', response_model=list[schemas.UserAdmin])
async def get_all_users(current_user: Annotated[schemas.User,
                        Depends(targefy_app.authenticaton.validation.get_current_user)],
                        db: Session = Depends(get_db),
                        ):
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail='You have no rights for this')
    users_model = db.query(models.User).all()
    return users_model


@router.put('/update_user_role/{user_id}', response_model=schemas.UserAdmin)
async def update_user_role(user_id: int,
                           user_role: str,
                           current_user: Annotated[schemas.User, Depends(
                               targefy_app.authenticaton.validation.get_current_user)],
                           db: Session = Depends(get_db),
                           ):
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail='You have no rights for this')

    user_model = db.query(models.User).filter(models.User.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail='User not found')

    if user_model.role == user_role:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail='The user has already been assigned this role',
                            )

    user_model.role = user_role
    db.add(user_model)
    db.commit()
    return user_model


@router.delete('/delete_user/{user_id}')
async def delete_user(user_id: int,
                      current_user: Annotated[schemas.User, Depends(
                          targefy_app.authenticaton.validation.get_current_user)],
                      db: Session = Depends(get_db),
                      ):
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail='You have no rights for this')

    user_model = db.query(models.User).filter(models.User.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail='User not found')
    db.delete(user_model)
    db.commit()
    return {'msg': 'User successfully deleted'}
