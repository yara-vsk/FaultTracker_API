from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer

from src.database import Base


class Image(Base):
    __tablename__ = "image"
    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(500), unique=True)
    fault_id: Mapped[int] = mapped_column(ForeignKey("fault.id"))

    def __repr__(self) -> str:
        return f"Image(id={self.id!r})"


class Fault(Base):
    __tablename__ = "fault"
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    images: Mapped[List["Image"]] = relationship(cascade="all, delete, delete-orphan")
    creator_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete="cascade"))
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id", ondelete="cascade"))

    def __repr__(self) -> str:
        return f"Fault(id={self.id!r})"

