from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.project.models import Project


async def get_project(project_id, session):
    stmt = select(Project).where(Project.id == project_id)
    project = await session.scalar(stmt)
    return project


async def get_projects(session, user_id):
    stmt = select(Project).where(Project.creator_id == user_id)
    projects = await session.execute(stmt)
    return projects.scalars().all()


async def create_project(project, user_id, session):
    project = Project(**project.dict(), creator_id=user_id)
    session.add(project)
    await session.commit()
    return project