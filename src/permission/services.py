from sqlalchemy import select
from sqlalchemy.orm import selectinload, contains_eager
from src.permission.models import Permission, UserPermission


async def create_permission(perm_pd, session):
    permission = Permission(**perm_pd.dict())
    session.add(permission)
    await session.commit()
    return permission


async def add_user_permission(permission, user, session):
    user_perm = UserPermission(user_id=user.id, permission_id=permission.id)
    session.add(user_perm)
    await session.commit()
    return user_perm


async def check_user_perms(user, codename, session):
    stmt = select(UserPermission).join(Permission,UserPermission.permission_id == Permission.id).\
        where(UserPermission.user_id == user.id).\
        where(Permission.codename == codename)#.options(contains_eager(UserPermission.permission_id))
    user_perms = await session.execute(stmt)
    return user_perms.scalar()