import datetime
import decimal

from fastapi import HTTPException
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session
from starlette import status

import models
import schemas
from targefy_app.authenticaton.utility import hash_password

today = datetime.date.today()


def get_user(db: Session, user_id: int):
    user_model = db.query(models.User).filter(models.User.id == user_id).first
    if user_model is None:
        return {'detail': 'User not found, invalid '}
    return user_model


def get_user_by_email(db: Session, email: str, username: str):
    return db.query(models.User).filter(
        (models.User.email == email) | (models.User.username == username)
    ).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, username: str, email: str, password: str):
    hashed_password = hash_password(password)
    user_model = models.User(username=username, email=email, hashed_password=hashed_password)
    db.add(user_model)
    db.commit()
    db.refresh(user_model)


def create_target(db: Session, value: float, user: schemas.User, record_id: int):
    latest_target = db.query(models.Target). \
        filter((models.Target.owner_id == user.id) | (models.Target.record_id == record_id)). \
        order_by(desc(models.Target.added_at)).first()
    if not latest_target:
        target_model = models.Target(value=value, owner_id=user.id, record_id=record_id)
        db.add(target_model)
        db.commit()
        db.refresh(target_model)
        targets_model = db.query(models.Target).filter(models.Target.owner_id == user.id). \
            order_by(desc(models.Target.added_at)).all()
        return targets_model
    elif latest_target.added_at == today:
        target_model = db.query(models.Target).filter(models.Target.added_at == today,
                                                      models.Target.owner_id == user.id,
                                                      models.Target.record_id == record_id).first()
        target_model.value = target_model.value + float(value)
        db.add(target_model)
        db.commit()
        return target_model


def get_target_model(db: Session, user: schemas.User, target_id: int, record_id: int):
    target_model = db.query(models.Target).filter(
        models.Target.owner_id == user.id,
        models.Target.id == target_id,
        models.Target.record_id == record_id,
    ).first()
    if target_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found or not enough rights to update')
    return target_model


def read_all_targets(db: Session, user: schemas.User, record_id: int):
    targets_model = db.query(models.Target).\
        filter((models.Target.owner_id == user.id), (models.Target.record_id == record_id)).\
        order_by(desc(models.Target.added_at)).all()

    if not targets_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found or not enough rights to read')

    last_target_date = targets_model[0].added_at
    days_diff = int(str(today - last_target_date)[0])

    if days_diff > 0:

        for i in range(days_diff):
            added_at = last_target_date + datetime.timedelta(days=i+1)
            target_model = models.Target(value=0.0, owner_id=user.id, added_at=added_at, record_id=record_id)
            db.add(target_model)
            db.commit()
            db.refresh(target_model)
        targets_model = db.query(models.Target). \
            filter((models.Target.owner_id == user.id), (models.Target.record_id == record_id)). \
            order_by(desc(models.Target.added_at)).all()

        return targets_model

    return targets_model


def update_target(db: Session, user: schemas.User, target_id: int, record_id: int):
    target_model = db.query(models.Target).filter(
        models.Target.owner_id == user.id,
        models.Target.id == target_id, models.Target.record_id == record_id).first()
    return target_model


def delete_target(db: Session, user: schemas.User, target_id: int):
    target_model = db.query(models.Target).filter(
        models.Target.owner_id == user.id,
        models.Target.id == target_id).first()
    return target_model


def create_record(db: Session, user: schemas.User, record_name: str, record_unit: str):
    record_model = models.Record(owner_id=user.id, record_name=record_name, unit=record_unit)
    db.add(record_model)
    db.commit()
    target_model = models.Target(owner_id=user.id, record_id=record_model.id, value=0.0)
    db.add(record_model)
    db.add(target_model)
    db.commit()


def read_all_records(user: schemas.User, db: Session, sort_by: str, order: str):
    records_model = db.query(models.Record).filter(models.Record.owner_id == user.id)
    if sort_by == 'date_added':
        if order == 'asc':
            records_model = records_model.order_by(models.Record.added_at.asc()).all()
        elif order == 'desc':
            records_model = records_model.order_by(models.Record.added_at.desc()).all()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='invalid order')
    elif sort_by == 'name':
        if order == 'asc':
            records_model = records_model.order_by(models.Record.record_name.asc()).all()
        elif order == 'desc':
            records_model = records_model.order_by(models.Record.record_name.desc()).all()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='invalid order')
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='invalid sort_by')
    if not records_model:
        create_record(db=db, user=user, record_name='Record', record_unit='units')
        records_model = db.query(models.Record).filter(models.Record.owner_id == user.id).all()
        return records_model
    return records_model


def get_record_model(user: schemas.User, record_id: int, db: Session):
    record_model = db.query(models.Record).filter(models.Record.id == record_id,
                                                  models.Record.owner_id == user.id,
                                                  ).first()
    if record_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Record does not exist or you have no rights to read it')

    return record_model


def delete_record_model(user: schemas.User, record_id: int, db: Session):
    record_model = get_record_model(user=user, record_id=record_id, db=db)
    targets_model = read_all_targets(user=user, record_id=record_id, db=db)
    for target in targets_model:
        db.delete(target)
    db.delete(record_model)
    db.commit()


def read_record_name(user: schemas.User, record_id: int, db: Session):
    record_model = get_record_model(user=user, db=db, record_id=record_id)
    return record_model.record_name


def read_record_unit(user: schemas.User, record_id: int, db: Session):
    record_model = get_record_model(user=user, db=db, record_id=record_id)
    return record_model.unit
