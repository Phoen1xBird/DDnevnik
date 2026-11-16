from .base import (
    EntityId,
    InputSchema,
    Name,
    Pagination,
    ScoreMaximum,
)


class AddCriterion(InputSchema):
    name: Name
    max_score: ScoreMaximum


class GetCriterion(InputSchema):
    criterion_id: EntityId


class ListCriteria(Pagination):
    pass


class EditCriterion(InputSchema):
    criterion_id: EntityId
    new_name: Name | None = None
    max_score: ScoreMaximum | None = None


class DeleteCriterion(InputSchema):
    criterion_id: EntityId
