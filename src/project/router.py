from typing import List

from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.background import BackgroundTasks

from src.auth.manager import current_active_user
from src.auth.schemas import UserRead
from src.database import get_async_session
from src.fault.router import fault_router
from src.permission.schemas import PermissionCreate
from src.permission.services import create_permission, add_user_permission, delete_permission, \
    get_permission_by_codename, delete_user_permission
from src.project.dependencies import valid_project, project_with_user_perm, valid_user, valid_member_role, \
    valid_user_without_perm, project_with_creator_perm, valid_user_with_perm
from fastapi_cache.decorator import cache

from src.project.schemas import ProjectRead, ProjectCreate, ProjectMemberRead, ProjectMemberOUT, MemberRoleRead
from src.project.services import create_project, get_projects, delete_project, update_project, create_project_member, \
    get_project_members_srv, get_project_member_srv, get_member_role_by_id, delete_project_member_src

project_router = APIRouter(
    prefix="/project",
    tags=['Project']
)


@project_router.delete('/{project_id}/member', response_model=ProjectMemberOUT)
async def delete_project_member(
        user=Depends(valid_user_with_perm),
        project=Depends(project_with_creator_perm),
        session: AsyncSession = Depends(get_async_session)
):

    project_member = await get_project_member_srv(project.id, user.id, session)
    member_role = await get_member_role_by_id(project_member.member_role_id, session)
    project_member_pd = ProjectMemberOUT(
        id=project_member.id,
        user=UserRead(**user.__dict__),
        project=ProjectRead(**project.__dict__),
        member_role=MemberRoleRead(**member_role.__dict__)
    )
    permission = await get_permission_by_codename(codename=f'project_{project.id}', session=session)
    await delete_project_member_src(project_member, session)
    await delete_user_permission(permission.id, user.id, session)
    return project_member_pd


@project_router.post('/{project_id}/member', response_model=ProjectMemberOUT)
async def add_project_member(
        user=Depends(valid_user_without_perm),
        member_role=Depends(valid_member_role),
        project=Depends(project_with_creator_perm),
        session: AsyncSession = Depends(get_async_session)
):
    permission = await get_permission_by_codename(codename=f'project_{project.id}', session=session)
    await add_user_permission(permission, user, session)
    new_project_member = await create_project_member(project.id, user.id, member_role.name, session)
    new_project_member_pd = ProjectMemberOUT(
        id=new_project_member.id,
        user=UserRead(**user.__dict__),
        project=ProjectRead(**project.__dict__),
        member_role=MemberRoleRead(**member_role.__dict__)
    )
    return new_project_member_pd


@project_router.get('/{project_id}/member', response_model=List[ProjectMemberOUT])
async def get_project_members(
        project=Depends(project_with_user_perm),
        session: AsyncSession = Depends(get_async_session)
):
    project_members = await get_project_members_srv(project.id, session)
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


