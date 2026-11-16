from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

from . import course
from . import mark
from . import student


class Enrollment(Base):
    __tablename__ = "enrollments"

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True, index=True
    )

    student: Mapped["student.Student"] = relationship(back_populates="enrollments")
    course: Mapped["course.Course"] = relationship(back_populates="enrollments")
    marks: Mapped[list["mark.Mark"]] = relationship(
        back_populates="enrollment", viewonly=True
    )
