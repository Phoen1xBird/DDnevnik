from dataclasses import InitVar, dataclass
from math import isfinite

from ddnevnik.errors import RuleViolationError


@dataclass(frozen=True)
class MaxScore:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise RuleViolationError("Максимальный балл должен быть положительным")


@dataclass(frozen=True)
class Score:
    value: int
    maximum: InitVar[MaxScore]

    def __post_init__(self, maximum: MaxScore) -> None:
        if self.value < 0:
            raise RuleViolationError("Балл не может быть отрицательным")
        if self.value > maximum.value:
            raise RuleViolationError(
                f"Оценка должна быть в диапазоне от 0 до {maximum.value}"
            )


@dataclass(frozen=True)
class Weight:
    value: float

    def __post_init__(self) -> None:
        if not isfinite(self.value) or self.value <= 0:
            raise RuleViolationError("Вес критерия должен быть конечным положительным числом")
