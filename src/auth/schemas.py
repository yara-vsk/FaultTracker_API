

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    id: int
    username: str


class UserCreate(schemas.BaseUserCreate):
    id: int
    username: str


class UserUpdate(schemas.BaseUserUpdate):
    id: int
    username: str
