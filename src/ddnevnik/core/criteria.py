from ddnevnik.errors import RuleViolationError
from ddnevnik.models import Criterion, MaxScore
from ddnevnik.schemas.criteria import (
    AddCriterion,
    GetCriterion,
    ListCriteria,
    EditCriterion,
    DeleteCriterion,
)
from ddnevnik.schemas.repositories import CriteriaRepository
from ddnevnik.schemas.results import CriterionResult
from ddnevnik.utils.route import route

from .base import API


class CriteriaAPI(API[CriteriaRepository]):
    @route("add")
    def add_criterion(self, request: AddCriterion) -> CriterionResult:
        criterion = self.repository.save(Criterion(**request.model_dump()))
        return CriterionResult.model_validate(criterion)

    @route("get")
    def get_criterion(self, request: GetCriterion) -> CriterionResult:
        criterion = self.repository.get(request.criterion_id)
        return CriterionResult.model_validate(criterion)

    @route("list")
    def list_criteria(self, request: ListCriteria) -> list[CriterionResult]:
        criteria = self.repository.list(limit=request.limit, offset=request.offset)
        return [CriterionResult.model_validate(criterion) for criterion in criteria]

    @route("edit")
    def edit_criterion(self, request: EditCriterion) -> CriterionResult:
        if request.new_name is None and request.max_score is None:
            raise RuleViolationError("Укажите новое имя или максимальный балл критерия")
        criterion = self.repository.get(request.criterion_id)
        if request.max_score is not None:
            criterion.change_maximum(
                MaxScore(request.max_score),
                self.repository.get_highest_mark(request.criterion_id),
            )
        if request.new_name is not None:
            criterion.name = request.new_name
        return CriterionResult.model_validate(self.repository.save(criterion))

    @route("delete")
    def delete_criterion(self, request: DeleteCriterion) -> CriterionResult:
        criterion = self.repository.get(request.criterion_id)
        result = CriterionResult.model_validate(criterion)
        self.repository.delete(criterion)
        return result
