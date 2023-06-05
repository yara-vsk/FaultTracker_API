from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from src.database import Base


class Permission(Base):
    __tablename__ = "permission"
    id: Mapped[int] = mapped_column(primary_key=True)
    codename: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)

    def __repr__(self) -> str:
        return f"Permission(id={self.id!r})"


class UserPermission(Base):
    __tablename__ = "userpermission"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete="cascade"))
    permission_id: Mapped[int] = mapped_column(ForeignKey('permission.id', ondelete="cascade"))

    def __repr__(self) -> str:
        return f"UserPermission(id={self.id!r})"