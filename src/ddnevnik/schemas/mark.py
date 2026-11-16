from .base import (
    EntityId,
    InputSchema,
    Pagination,
    ScoreValue,
)


class AddMark(InputSchema):
    student_id: EntityId
    course_id: EntityId
    criterion_id: EntityId
    value: ScoreValue


class GetMark(InputSchema):
    student_id: EntityId
    course_id: EntityId
    criterion_id: EntityId


class ListMarks(Pagination):
    pass


class EditMark(InputSchema):
    student_id: EntityId
    course_id: EntityId
    criterion_id: EntityId
    value: ScoreValue


class DeleteMark(InputSchema):
    student_id: EntityId
    course_id: EntityId
    criterion_id: EntityId


class GetStudentMarks(InputSchema):
    student_id: EntityId
    course_id: EntityId
