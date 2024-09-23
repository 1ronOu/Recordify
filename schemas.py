from pydantic import BaseModel, constr, ConfigDict
from datetime import datetime


class Target(BaseModel):
    id: int
    value: float
    added_at: datetime
    owner_id: int


class TargetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    value: float
    added_at: datetime


# USER_SCHEMAS


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: str
    username: constr(min_length=3, max_length=21)


class UserAdmin(UserBase):
    id: int
    is_active: bool
    role: str


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool = True
    role: str = 'user'
    password: str

