from fastapi import HTTPException, UploadFile, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.auth.manager import current_active_user, get_user_manager
from src.database import get_async_session
from src.permission.services import check_user_perms
from src.project.models import Project
from src.project.services import get_project, get_projects, get_user_project_role, get_member_role


async def valid_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    project = await get_project(project_id, session)
    if not project:
        raise HTTPException(status_code=404, detail="Not found.")
    return project


async def project_with_user_perm(
        request: Request,
        project: Project = Depends(valid_project),
        session: AsyncSession = Depends(get_async_session),
        user=Depends(current_active_user)
):
    perm_codename = f'project_{project.id}'
    user_has_perms = await check_user_perms(user, perm_codename, session)
    if not user_has_perms:
        raise HTTPException(status_code=404, detail="Not found.")
    user_project_role = await get_user_project_role(project.id, user.id, session)
    if request.method == 'PUT' and user_project_role.name == 'reader':
        raise HTTPException(status_code=404, detail="Not found.")
    if request.method == 'DELETE' and project.creator_id != user.id:
        raise HTTPException(status_code=404, detail="Not found.")
    return project


async def project_with_creator_perm(
        project: Project = Depends(project_with_user_perm),
        user=Depends(current_active_user)
):
    if user.id != project.creator_id:
        raise HTTPException(status_code=450, detail="You don't have permission.")
    return project


async def valid_user(
        user_email=Body(description="enter the member's email address"),
        user_manager=Depends(get_user_manager)
):
    user = await user_manager.get_by_email(user_email)
    if not user:
        raise HTTPException(status_code=404, detail="Not found.")
    return user


async def valid_user_without_perm(
        user=Depends(valid_user),
        project: Project = Depends(valid_project),
        session: AsyncSession = Depends(get_async_session),
):
    perm_codename = f'project_{project.id}'
    user_has_perms = await check_user_perms(user, perm_codename, session)
    if user_has_perms:
        raise HTTPException(status_code=454, detail=f"User '{user.email}' is a member of project {project.name}.")
    if user.id == project.creator_id:
        raise HTTPException(status_code=453, detail="Project creator cannot be deleted or changed his role.")
    return user


async def valid_user_with_perm(
        user=Depends(valid_user),
        project: Project = Depends(valid_project),
        session: AsyncSession = Depends(get_async_session),
):
    perm_codename = f'project_{project.id}'
    user_has_perms = await check_user_perms(user, perm_codename, session)
    if not user_has_perms:
        raise HTTPException(status_code=454, detail=f"User '{user.email}' is not a member of project {project.name}.")
    if user.id == project.creator_id:
        raise HTTPException(status_code=453, detail="Project creator cannot be deleted or changed his role.")
    return user


async def valid_member_role(
        member_role_name: str = Body(max_length=300, description="enter the member's role"),
        session: AsyncSession = Depends(get_async_session),
):
    member_role = await get_member_role(member_role_name, session)
    if not member_role:
        raise HTTPException(status_code=404, detail="Not found.")
    return member_role