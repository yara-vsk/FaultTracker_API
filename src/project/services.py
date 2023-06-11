from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.auth.models import User
from src.auth.schemas import UserRead
from src.database import async_session_maker
from src.project.models import Project, MemberRole, ProjectMember
from src.project.schemas import ProjectMemberOUT, ProjectRead, MemberRoleRead


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
    stmt = select(
        ProjectMember.id.label('ProjectMember_id'),
        User.id.label('User_id'),
        User.username.label('User_username'),
        User.email.label('User_email'),
        User.is_active.label('User_is_active'),
        User.is_superuser.label('User_is_superuser'),
        User.is_verified.label('User_is_verified'),
        Project.id.label('Project_id'),
        Project.name.label('Project_name'),
        Project.create_date.label('Project_create_date'),
        Project.creator_id.label('Project_creator_id'),
        MemberRole.id.label('MemberRole_id'),
        MemberRole.name.label('MemberRole_name')
    ).\
        join_from(ProjectMember, MemberRole, MemberRole.id == ProjectMember.member_role_id).\
        join(User, User.id == ProjectMember.user_id). \
        join(Project, Project.id == ProjectMember.project_id). \
        where(ProjectMember.project_id == project_id)
    project_members = await session.execute(stmt)
    results = project_members.all()
    columns = project_members.keys()
    project_member_objects = []
    for row in results:
        project_member_dict = dict(zip(columns, row))
        project_member = ProjectMemberOUT(
            id=project_member_dict['ProjectMember_id'],
            user=UserRead(
                id=project_member_dict['User_id'],
                username=project_member_dict['User_username'],
                email=project_member_dict['User_email'],
                is_active=project_member_dict['User_is_active'],
                is_superuser=project_member_dict['User_is_superuser'],
                is_verified=project_member_dict['User_is_verified'],
            ),
            project=ProjectRead(
                id=project_member_dict['Project_id'],
                name=project_member_dict['Project_name'],
                create_date=project_member_dict['Project_create_date'],
                creator_id=project_member_dict['Project_creator_id']
            ),
            member_role=MemberRoleRead(
                id=project_member_dict['MemberRole_id'],
                name=project_member_dict['MemberRole_name']
            )
        )
        project_member_objects.append(project_member)
    return project_member_objects


async def get_user_project_role(project_id, user_id, session):
    stmt = select(MemberRole).join(ProjectMember, MemberRole.id == ProjectMember.member_role_id).\
        where(ProjectMember.user_id == user_id, ProjectMember.project_id == project_id)
    member_role = await session.scalar(stmt)
    await session.commit()
    return member_role