from typing import List, Union, Callable

from pydantic import BaseModel, validator, Field


class PermissionCreate(BaseModel):
    codename: str
    name: str

    class Config:
        orm_mode = True


class PermissionRead(PermissionCreate):
    id: int


class UserPermissionCreate(BaseModel):
    creator_id: int
    permission_id: int

    class Config:
        orm_mode = True


class UserPermissionRead(UserPermissionCreate):
    id: int