from fastapi import HTTPException, UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.auth.manager import current_active_user
from src.database import get_async_session
from src.permission.services import check_user_perms
from src.project.models import Project
from src.project.services import get_project, get_projects, get_user_project_role


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