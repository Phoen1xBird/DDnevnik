from collections import Counter

from ddnevnik.schemas.repositories import CourseRepository, StudentRepository
from ddnevnik.schemas.results import (
    CourseCriterionResult,
    CourseTotalsResult,
    GetCourseResults,
    GetStudentCourseResults,
    GetStudentResults,
    MarkResult,
    TotalResult,
)
from ddnevnik.utils.route import route
from ddnevnik.workers.scoring import TotalCalculator, create_strategy

from .base import API


class ResultsAPI(API[CourseRepository]):
    def __init__(
        self, repository: CourseRepository, student_repository: StudentRepository
    ) -> None:
        self.student_repository = student_repository
        self.calculator = TotalCalculator()
        super().__init__(repository)

    @route("course")
    def get_course_results(self, request: GetCourseResults) -> CourseTotalsResult:
        self.calculator.set_strategy(create_strategy(request.strategy))
        self.repository.get(request.course_id)
        rubric = self.repository.get_rubric(request.course_id)
        criterion_columns = {
            criterion.criterion_id: f"{criterion.name} (max {criterion.max_score})"
            for criterion in rubric
        }
        label_counts = Counter(criterion_columns.values())
        for criterion_id, label in criterion_columns.items():
            if label_counts[label] > 1:
                criterion_columns[criterion_id] = f"{label} [id {criterion_id}]"
        columns = ["id", "student_name", *criterion_columns.values(), "total"]

        marks_by_student: dict[int, list[MarkResult]] = {}
        for mark in self.repository.get_marks(request.course_id):
            marks_by_student.setdefault(mark.student_id, []).append(
                MarkResult.model_validate(mark)
            )

        rows: list[dict[str, int | float | str | None]] = []
        for student in self.repository.get_students(request.course_id, limit=None):
            marks = marks_by_student.get(student.id, [])
            values = {mark.criterion_id: mark.value for mark in marks}
            row: dict[str, int | float | str | None] = {
                "id": student.id,
                "student_name": student.name,
            }
            for criterion in rubric:
                row[criterion_columns[criterion.criterion_id]] = values.get(
                    criterion.criterion_id, 0
                )
            row["total"] = self.calculator.calculate(
                student.id, request.course_id, rubric, marks
            ).total_score
            rows.append(row)

        return CourseTotalsResult(columns=columns, rows=rows)

    @route("student")
    def get_student_results(self, request: GetStudentResults) -> list[TotalResult]:
        self.calculator.set_strategy(create_strategy(request.strategy))
        self.student_repository.get(request.student_id)
        courses = self.student_repository.get_courses(request.student_id, limit=None)
        if not courses:
            return []

        rubrics: dict[int, list[CourseCriterionResult]] = {course.id: [] for course in courses}
        marks: dict[int, list[MarkResult]] = {course.id: [] for course in courses}
        for criterion in self.student_repository.get_rubrics(request.student_id):
            rubrics[criterion.course_id].append(criterion)
        for mark in self.student_repository.get_marks(request.student_id):
            marks[mark.course_id].append(MarkResult.model_validate(mark))

        return [
            self.calculator.calculate(request.student_id, course.id, rubrics[course.id], marks[course.id])
            for course in courses
        ]

    @route("student-course")
    def get_student_course_results(self, request: GetStudentCourseResults) -> TotalResult:
        self.calculator.set_strategy(create_strategy(request.strategy))
        self.repository.get_student(request.student_id)
        self.repository.get(request.course_id)
        self.repository.get_enrollment(request.student_id, request.course_id)
        rubric = self.repository.get_rubric(request.course_id)
        marks = [
            MarkResult.model_validate(mark)
            for mark in self.repository.get_marks(
                request.course_id, student_id=request.student_id
            )
        ]
        return self.calculator.calculate(request.student_id, request.course_id, rubric, marks)
