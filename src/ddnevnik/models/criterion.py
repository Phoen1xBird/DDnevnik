from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, composite, mapped_column, relationship

from ddnevnik.errors import RuleViolationError

from .base import Base
from .value_objects import MaxScore

from . import course_criterion


class Criterion(Base):
    __tablename__ = "criteria"
    __table_args__ = (
        CheckConstraint("max_score > 0", name="ck_criteria_max_score_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    _max_score: Mapped[int] = mapped_column("max_score", Integer)
    _maximum: Mapped[MaxScore] = composite(MaxScore, _max_score)

    course_links: Mapped[list["course_criterion.CourseCriterion"]] = relationship(
        back_populates="criterion", passive_deletes="all"
    )

    @hybrid_property
    def maximum(self) -> MaxScore:
        return self._maximum

    @maximum.setter
    def maximum(self, maximum: MaxScore) -> None:
        if self._max_score is not None and maximum.value < self._max_score:
            raise RuleViolationError(
                "Для уменьшения максимума используйте change_maximum с проверкой оценок"
            )
        self._maximum = maximum

    @maximum.expression
    def maximum(cls):
        return cls._maximum

    @hybrid_property
    def max_score(self) -> int:
        return self.maximum.value

    @max_score.setter
    def max_score(self, value: int) -> None:
        self.maximum = MaxScore(value)

    @max_score.expression
    def max_score(cls):
        return cls._max_score

    def change_maximum(self, maximum: MaxScore, highest_mark: int | None) -> None:
        if highest_mark is not None and maximum.value < highest_mark:
            raise RuleViolationError(
                f"Максимум нельзя уменьшить ниже выставленной оценки {highest_mark}"
            )
        self._maximum = maximum
