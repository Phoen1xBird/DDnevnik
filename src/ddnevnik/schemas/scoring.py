from typing import Protocol

from .results import CourseCriterionResult, MarkResult


class TotalStrategy(Protocol):
    def calculate(
        self,
        rubric: list[CourseCriterionResult],
        marks: list[MarkResult],
    ) -> float | None: ...
