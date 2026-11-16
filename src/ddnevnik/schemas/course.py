from .base import (
    EntityId,
    InputSchema,
    Name,
    Pagination,
    Weight,
)


class AddCourse(InputSchema):
    name: Name


class GetCourse(InputSchema):
    course_id: EntityId


class ListCourses(Pagination):
    pass


class EditCourse(InputSchema):
    course_id: EntityId
    new_name: Name


class DeleteCourse(InputSchema):
    course_id: EntityId


class AddStudent(InputSchema):
    course_id: EntityId
    student_id: EntityId


class AddCriterion(InputSchema):
    course_id: EntityId
    criterion_id: EntityId
    weight: Weight


class GetStudents(Pagination):
    course_id: EntityId


class GetCriteria(InputSchema):
    course_id: EntityId
