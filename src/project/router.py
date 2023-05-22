from typing import List

from fastapi import APIRouter, Depends, UploadFile, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.background import BackgroundTasks

from src.auth.manager import current_active_user
from src.database import get_async_session
from src.project.dependencies import valid_project
from fastapi_cache.decorator import cache

from src.project.schemas import ProjectRead, ProjectCreate
from src.project.services import create_project, get_projects

project_router = APIRouter(
    prefix="/project",
    tags=['Project']
)


@project_router.get('/{project_id}', response_model=ProjectRead)
async def get_user_project_by_id(
        project=Depends(valid_project)
):
    return project


@project_router.post('/', response_model=ProjectRead)
async def create_user_project(
        project: ProjectCreate,
        session: AsyncSession = Depends(get_async_session),
        user=Depends(current_active_user)
):
    project = await create_project(project, user.id, session)
    return project


@project_router.get('/', response_model=List[ProjectRead])
async def get_user_projects(
        session: AsyncSession = Depends(get_async_session),
        user=Depends(current_active_user)
):
    projects = await get_projects(session, user.id)
    return projects