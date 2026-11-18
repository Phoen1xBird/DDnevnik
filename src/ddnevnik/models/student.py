from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

from . import enrollment


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))

    enrollments: Mapped[list["enrollment.Enrollment"]] = relationship(
        back_populates="student", passive_deletes="all"
    )
