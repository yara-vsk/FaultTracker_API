from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from src.auth.auth import auth_backend
from src.auth.manager import fastapi_users
from src.auth.schemas import UserRead, UserCreate
from src.config import REDIS_HOST, REDIS_PORT
from src.fault.router import fault_router

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend


from redis import asyncio as aioredis

from src.tasks.router import tasks_router

app = FastAPI()


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)


app.include_router(fault_router)
app.include_router(tasks_router)

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")







