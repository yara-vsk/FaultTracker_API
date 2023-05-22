from fastapi import HTTPException, UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.manager import current_active_user
from src.database import get_async_session
from src.project.services import get_project, get_projects


async def valid_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
        user=Depends(current_active_user),
):
    project = await get_project(project_id, session)
    if not project or project.creator_id != user.id:
        raise HTTPException(status_code=404, detail="Not found.")
    return project