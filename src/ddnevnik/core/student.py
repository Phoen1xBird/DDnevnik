from ddnevnik.errors import AlreadyExistsError
from ddnevnik.models import Student
from ddnevnik.schemas.repositories import StudentRepository
from ddnevnik.schemas.results import (
    CourseResult,
    EnrollmentResult,
    MarkResult,
    StudentResult,
)
from ddnevnik.schemas.student import (
    AddStudent,
    GetStudent,
    ListStudents,
    EditStudent,
    DeleteStudent,
    AddCourse,
    GetCourses,
    GetMarks,
)
from ddnevnik.utils.route import route

from .base import API


class StudentAPI(API[StudentRepository]):
    @route("add")
    def add_student(self, request: AddStudent) -> StudentResult:
        student = self.repository.save(Student(name=request.name))
        return StudentResult.model_validate(student)

    @route("get")
    def get_student(self, request: GetStudent) -> StudentResult:
        student = self.repository.get(request.student_id)
        return StudentResult.model_validate(student)

    @route("list")
    def list_students(self, request: ListStudents) -> list[StudentResult]:
        students = self.repository.list(limit=request.limit, offset=request.offset)
        return [StudentResult.model_validate(student) for student in students]

    @route("edit")
    def edit_student(self, request: EditStudent) -> StudentResult:
        student = self.repository.get(request.student_id)
        student.name = request.new_name
        return StudentResult.model_validate(self.repository.save(student))

    @route("delete")
    def delete_student(self, request: DeleteStudent) -> StudentResult:
        student = self.repository.get(request.student_id)
        result = StudentResult.model_validate(student)
        self.repository.delete(student)
        return result

    @route("add-course")
    def add_course(self, request: AddCourse) -> EnrollmentResult:
        self.repository.get(request.student_id)
        self.repository.get_course(request.course_id)
        if self.repository.find_enrollment(request.student_id, request.course_id) is not None:
            raise AlreadyExistsError("Студент уже зачислен на этот курс")
        enrollment = self.repository.add_enrollment(request.student_id, request.course_id)
        return EnrollmentResult.model_validate(enrollment)

    @route("get-courses")
    def get_courses(self, request: GetCourses) -> list[CourseResult]:
        self.repository.get(request.student_id)
        courses = self.repository.get_courses(
            request.student_id, limit=request.limit, offset=request.offset
        )
        return [CourseResult.model_validate(course) for course in courses]


    @route("get-marks")
    def get_marks(self, request: GetMarks) -> list[MarkResult]:
        self.repository.get(request.student_id)
        return [
            MarkResult.model_validate(mark)
            for mark in self.repository.get_marks(request.student_id)
        ]
