from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.auth.models import User
from src.database import async_session_maker
from src.project.models import Project, MemberRole, ProjectMember


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


async def delete_project(project, session):
    await session.delete(project)
    await session.commit()
    return


async def update_project(project, name, session):
    project.name = name
    await session.commit()
    return project


async def create_member_roles():
    async with async_session_maker() as session:
        stmt = select(MemberRole)
        roles = await session.execute(stmt)
        if not roles.scalars().all():
            role_1 = MemberRole(name='reader')
            role_2 = MemberRole(name='editor')
            session.add_all([role_1, role_2])
            await session.commit()
        return


async def create_project_member(project_id, user_id, role_name, session):
    stmt = select(MemberRole).where(MemberRole.name == role_name)
    role = await session.scalar(stmt)
    project_member = ProjectMember(project_id=project_id, user_id=user_id, member_role_id=role.id)
    session.add(project_member)
    await session.commit()
    return project_member


async def get_project_members_srv(project_id, session):
    stmt = select(ProjectMember).where(ProjectMember.project_id == project_id)
    project_members = await session.execute(stmt)
    return project_members.scalars().all()


async def get_user_project_role(project_id, user_id, session):
    stmt = select(MemberRole).join(ProjectMember, MemberRole.id == ProjectMember.member_role_id).\
        where(ProjectMember.user_id == user_id, ProjectMember.project_id==project_id)
    member_role = await session.scalar(stmt)
    await session.commit()
    return member_role