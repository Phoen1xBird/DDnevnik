from sqlalchemy import CheckConstraint, Float, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, composite, mapped_column, relationship

from .base import Base
from .value_objects import Weight

from . import course
from . import criterion
from . import mark


class CourseCriterion(Base):
    __tablename__ = "course_criteria"
    __table_args__ = (
        CheckConstraint("weight > 0", name="ck_course_criteria_weight_positive"),
    )

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True
    )
    criterion_id: Mapped[int] = mapped_column(
        ForeignKey("criteria.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    _weight: Mapped[float] = mapped_column("weight", Float)
    importance: Mapped[Weight] = composite(Weight, _weight)

    course: Mapped["course.Course"] = relationship(back_populates="rubric")
    criterion: Mapped["criterion.Criterion"] = relationship(back_populates="course_links")
    marks: Mapped[list["mark.Mark"]] = relationship(
        back_populates="course_criterion", viewonly=True
    )

    @hybrid_property
    def weight(self) -> float:
        return self.importance.value

    @weight.setter
    def weight(self, value: float) -> None:
        self.importance = Weight(value)

    @weight.expression
    def weight(cls):
        return cls._weight
