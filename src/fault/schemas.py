from datetime import datetime
from typing import List, Union, Callable

from pydantic import BaseModel, validator, Field

from src.auth.schemas import UserRead


class ImageRead(BaseModel):
    id: int
    file_name: str
    link: Union[str, None] =None

    class Config:
        orm_mode = True


    @validator('link', pre=True, always=True)
    def set_link(cls, v, values, **kwargs):
        if v:
            return v
        v_new = '/image/' + str(values['id'])
        return v_new


class FaultRead(BaseModel):
    id: int
    description: str
    images: List["ImageRead"]
    creator_id: int
    create_date: datetime
    project_id: int

    class Config:
        orm_mode = True

