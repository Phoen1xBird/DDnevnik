from ddnevnik.errors import AlreadyExistsError
from ddnevnik.models import Course
from ddnevnik.schemas.course import (
    AddCourse,
    GetCourse,
    ListCourses,
    EditCourse,
    DeleteCourse,
    AddStudent,
    AddCriterion,
    GetStudents,
    GetCriteria,
)
from ddnevnik.schemas.repositories import CourseRepository
from ddnevnik.schemas.results import (
    CourseCriterionResult,
    CourseResult,
    EnrollmentResult,
    StudentResult,
)
from ddnevnik.utils.route import route

from .base import API


class CourseAPI(API[CourseRepository]):
    @route("add")
    def add_course(self, request: AddCourse) -> CourseResult:
        course = self.repository.save(Course(name=request.name))
        return CourseResult.model_validate(course)

    @route("get")
    def get_course(self, request: GetCourse) -> CourseResult:
        course = self.repository.get(request.course_id)
        return CourseResult.model_validate(course)

    @route("list")
    def list_courses(self, request: ListCourses) -> list[CourseResult]:
        courses = self.repository.list(limit=request.limit, offset=request.offset)
        return [CourseResult.model_validate(course) for course in courses]

    @route("edit")
    def edit_course(self, request: EditCourse) -> CourseResult:
        course = self.repository.get(request.course_id)
        course.name = request.new_name
        return CourseResult.model_validate(self.repository.save(course))

    @route("delete")
    def delete_course(self, request: DeleteCourse) -> CourseResult:
        course = self.repository.get(request.course_id)
        result = CourseResult.model_validate(course)
        self.repository.delete(course)
        return result

    @route("add-student")
    def add_student(self, request: AddStudent) -> EnrollmentResult:
        self.repository.get(request.course_id)
        self.repository.get_student(request.student_id)
        if self.repository.find_enrollment(request.student_id, request.course_id) is not None:
            raise AlreadyExistsError("Студент уже зачислен на этот курс")
        enrollment = self.repository.add_enrollment(request.student_id, request.course_id)
        return EnrollmentResult.model_validate(enrollment)

    @route("add-criterion")
    def add_criterion(self, request: AddCriterion) -> CourseCriterionResult:
        self.repository.get(request.course_id)
        criterion = self.repository.get_criterion(request.criterion_id)
        if self.repository.find_criterion(request.course_id, request.criterion_id) is not None:
            raise AlreadyExistsError("Критерий уже добавлен в этот курс")
        link = self.repository.add_criterion(
            request.course_id, request.criterion_id, request.weight
        )
        return CourseCriterionResult(
            course_id=link.course_id,
            criterion_id=link.criterion_id,
            name=criterion.name,
            max_score=criterion.max_score,
            weight=link.weight,
        )

    @route("get-students")
    def get_students(self, request: GetStudents) -> list[StudentResult]:
        self.repository.get(request.course_id)
        students = self.repository.get_students(
            request.course_id, limit=request.limit, offset=request.offset
        )
        return [StudentResult.model_validate(student) for student in students]

    @route("get-criteria")
    def get_criteria(self, request: GetCriteria) -> list[CourseCriterionResult]:
        self.repository.get(request.course_id)
        return self.repository.get_rubric(request.course_id)
