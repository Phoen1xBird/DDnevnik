from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

from . import course_criterion
from . import enrollment


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))

    enrollments: Mapped[list["enrollment.Enrollment"]] = relationship(
        back_populates="course", passive_deletes="all"
    )
    rubric: Mapped[list["course_criterion.CourseCriterion"]] = relationship(
        back_populates="course", passive_deletes="all"
    )
