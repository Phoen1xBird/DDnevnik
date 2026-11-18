from .base import (
    EntityId,
    InputSchema,
    Name,
    Pagination,
)


class AddStudent(InputSchema):
    name: Name


class GetStudent(InputSchema):
    student_id: EntityId


class ListStudents(Pagination):
    pass


class EditStudent(InputSchema):
    student_id: EntityId
    new_name: Name


class DeleteStudent(InputSchema):
    student_id: EntityId


class AddCourse(InputSchema):
    student_id: EntityId
    course_id: EntityId


class GetCourses(Pagination):
    student_id: EntityId


class GetMarks(InputSchema):
    student_id: EntityId
