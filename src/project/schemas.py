from datetime import datetime
from typing import List, Union, Callable

from pydantic import BaseModel, validator, Field
from src.auth.schemas import UserRead


class ProjectCreate(BaseModel):
    name: str

    class Config:
        orm_mode = True


class ProjectRead(ProjectCreate):
    id: int
    create_date: datetime
    creator_id: int

    class Config:
        orm_mode = True
