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

