from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.background import BackgroundTasks

from src.auth.manager import current_active_user
from src.auth.schemas import UserRead
from src.database import get_async_session
from src.fault.router import fault_router
from src.permission.schemas import PermissionCreate
from src.permission.services import create_permission, add_user_permission, delete_permission
from src.project.dependencies import valid_project, project_with_user_perm
from fastapi_cache.decorator import cache

from src.project.schemas import ProjectRead, ProjectCreate, ProjectMemberRead
from src.project.services import create_project, get_projects, delete_project, update_project, create_project_member, \
    get_project_members_srv

project_router = APIRouter(
    prefix="/project",
    tags=['Project']
)


@project_router.get('/{project_id}/member', response_model=List[ProjectMemberRead])
async def get_project_members(
        project=Depends(project_with_user_perm),
        session: AsyncSession = Depends(get_async_session)
):
    project_members = await get_project_members_srv(project.id, session)
    print(project_members)
    return project_members


@project_router.get('/{project_id}', response_model=ProjectRead)
async def get_project_by_id(
        project=Depends(project_with_user_perm)
):
    return project


@project_router.delete('/{project_id}', response_model=ProjectRead)
async def delete_project_by_id(
        project=Depends(project_with_user_perm),
        session: AsyncSession = Depends(get_async_session)
):
    await delete_permission(f'project_{project.id}', session)
    await delete_project(project, session)
    return project


@project_router.put('/{project_id}', response_model=ProjectRead)
async def update_project_by_id(
        project_new: ProjectCreate,
        project=Depends(project_with_user_perm),
        session: AsyncSession = Depends(get_async_session),
):
    project_updated = await update_project(project, project_new.name, session)
    return project_updated


@project_router.post('/', response_model=ProjectRead)
async def create_user_project(
        project: ProjectCreate,
        session: AsyncSession = Depends(get_async_session),
        user=Depends(current_active_user)
):
    project = await create_project(project, user.id, session)
    permission = await create_permission(
        PermissionCreate(
            codename=f'project_{project.id}',
            name=f'Can use [project] with [id] = {project.id}'
        ),
        session
    )
    await add_user_permission(permission, user, session)
    await create_project_member(project.id, user.id, 'editor', session)
    return project


@project_router.get('/', response_model=List[ProjectRead])
async def get_user_projects(
        session: AsyncSession = Depends(get_async_session),
        user=Depends(current_active_user)
):
    projects = await get_projects(session, user.id)
    return projects


