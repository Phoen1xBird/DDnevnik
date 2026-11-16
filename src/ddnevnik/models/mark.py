from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Index, Integer
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ddnevnik.errors import RuleViolationError

from .base import Base
from .value_objects import Score

from . import course_criterion
from . import criterion
from . import enrollment


class Mark(Base):
    __tablename__ = "marks"
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id", "course_id"],
            ["enrollments.student_id", "enrollments.course_id"],
            ondelete="CASCADE",
            name="fk_marks_enrollment",
        ),
        ForeignKeyConstraint(
            ["course_id", "criterion_id"],
            ["course_criteria.course_id", "course_criteria.criterion_id"],
            ondelete="CASCADE",
            name="fk_marks_course_criterion",
        ),
        CheckConstraint("value >= 0", name="ck_marks_value_nonnegative"),
        Index("ix_marks_course_criterion", "course_id", "criterion_id"),
    )

    student_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    criterion_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _value: Mapped[int] = mapped_column("value", Integer)

    enrollment: Mapped["enrollment.Enrollment"] = relationship(
        back_populates="marks", viewonly=True
    )
    course_criterion: Mapped["course_criterion.CourseCriterion"] = relationship(
        back_populates="marks", viewonly=True
    )

    @property
    def score(self) -> Score:
        return Score(self._value, self._get_criterion().maximum)

    @score.setter
    def score(self, score: Score) -> None:
        self.set_score(score, self._get_criterion())

    def _get_criterion(self) -> "criterion.Criterion":
        target = getattr(self, "_criterion_context", None)
        if target is None:
            link = self.course_criterion
            target = link.criterion if link is not None else None
        if target is None:
            raise RuleViolationError(
                "Для назначения балла нужен критерий; используйте Mark.create или set_score"
            )
        return target

    @hybrid_property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        self.set_score(value, self._get_criterion())

    @value.expression
    def value(cls):
        return cls._value

    @classmethod
    def create(
        cls,
        student_id: int,
        course_id: int,
        criterion: "criterion.Criterion",
        score: int | Score,
    ) -> "Mark":
        mark = cls(
            student_id=student_id, course_id=course_id, criterion_id=criterion.id
        )
        mark.set_score(score, criterion)
        return mark

    def set_score(self, score: int | Score, criterion: "criterion.Criterion") -> None:
        if criterion.id != self.criterion_id:
            raise RuleViolationError("Критерий не соответствует оценке")
        value = score.value if isinstance(score, Score) else score
        self._value = Score(value, criterion.maximum).value
        self._criterion_context = criterion
