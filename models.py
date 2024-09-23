from sqlalchemy import Column, String, Integer, Boolean, Date, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default='user')

    targets = relationship('Target', back_populates='owner')
    records = relationship('Record', back_populates='owner')


class Target(Base):
    __tablename__ = 'targets'

    id = Column(Integer, primary_key=True)
    value = Column(Float)
    added_at = Column(Date, server_default=func.now())
    owner_id = Column(Integer, ForeignKey('users.id'))
    record_id = Column(Integer, ForeignKey('records.id'))

    owner = relationship('User', back_populates='targets')
    record = relationship('Record', back_populates='targets')


class Record(Base):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    added_at = Column(Date, server_default=func.now())
    record_name = Column(String, default='Record')
    unit = Column(String, nullable=False, default='units')

    owner = relationship('User', back_populates='records')
    targets = relationship('Target', back_populates='record')

