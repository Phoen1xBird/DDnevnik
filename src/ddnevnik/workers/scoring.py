from ddnevnik.errors import RuleViolationError
from ddnevnik.schemas.results import CourseCriterionResult, MarkResult, TotalMethod, TotalResult
from ddnevnik.schemas.scoring import TotalStrategy


class WeightedTotalStrategy:
    def calculate(
        self, rubric: list[CourseCriterionResult], marks: list[MarkResult]
    ) -> float | None:
        if not rubric:
            return None
        values = {mark.criterion_id: mark.value for mark in marks}
        weighted_score = 0.0
        total_weight = 0.0
        for criterion in rubric:
            weighted_score += (
                criterion.weight * values.get(criterion.criterion_id, 0) / criterion.max_score
            )
            total_weight += criterion.weight
        return 100 * weighted_score / total_weight


class PointsTotalStrategy:
    def calculate(
        self, rubric: list[CourseCriterionResult], marks: list[MarkResult]
    ) -> float | None:
        if not rubric:
            return None
        values = {mark.criterion_id: mark.value for mark in marks}
        score = sum(values.get(criterion.criterion_id, 0) for criterion in rubric)
        maximum = sum(criterion.max_score for criterion in rubric)
        return 100 * score / maximum


def create_strategy(method: TotalMethod) -> TotalStrategy:
    if method == TotalMethod.WEIGHTED:
        return WeightedTotalStrategy()
    if method == TotalMethod.POINTS:
        return PointsTotalStrategy()
    raise RuleViolationError(f"Неизвестная стратегия расчёта: {method!r}")


class TotalCalculator:
    def __init__(self, strategy: TotalStrategy | None = None) -> None:
        self._strategy = strategy if strategy is not None else WeightedTotalStrategy()

    def set_strategy(self, strategy: TotalStrategy) -> None:
        self._strategy = strategy

    def calculate(
        self,
        student_id: int,
        course_id: int,
        rubric: list[CourseCriterionResult],
        marks: list[MarkResult],
    ) -> TotalResult:
        values = {mark.criterion_id: mark.value for mark in marks}
        total_score = self._strategy.calculate(rubric, marks)
        return TotalResult(
            student_id=student_id,
            course_id=course_id,
            total_score=round(total_score, 2) if total_score is not None else None,
            completed_criteria=sum(criterion.criterion_id in values for criterion in rubric),
            total_criteria=len(rubric),
        )


def calculate_total(
    student_id: int,
    course_id: int,
    rubric: list[CourseCriterionResult],
    marks: list[MarkResult],
) -> TotalResult:
    return TotalCalculator().calculate(student_id, course_id, rubric, marks)
