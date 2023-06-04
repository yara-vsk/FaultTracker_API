from datetime import datetime
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from src.database import Base


class Project(Base):
    __tablename__ = "project"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    creator_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete="cascade"))
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())

    def __repr__(self) -> str:
        return f"Project(id={self.id!r})"


class MemberRole(Base):
    __tablename__ = "member_role"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"MemberRole(id={self.id!r})"


class ProjectMember(Base):
    __tablename__ = "project_member"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete="cascade"))
    project_id: Mapped[int] = mapped_column(ForeignKey('project.id', ondelete="cascade"))
    member_role_id:Mapped[int] = mapped_column(ForeignKey('member_role.id', ondelete="cascade"))

    def __repr__(self) -> str:
        return f"ProjectMember(id={self.id!r})"