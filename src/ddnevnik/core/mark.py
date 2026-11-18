from ddnevnik.errors import AlreadyExistsError, RuleViolationError
from ddnevnik.models import Criterion, Mark
from ddnevnik.schemas.mark import (
    AddMark,
    GetMark,
    ListMarks,
    EditMark,
    DeleteMark,
    GetStudentMarks,
)
from ddnevnik.schemas.repositories import MarkRepository
from ddnevnik.schemas.results import MarkResult
from ddnevnik.utils.route import route

from .base import API


class MarkAPI(API[MarkRepository]):
    @route("add")
    def add_mark(self, request: AddMark) -> MarkResult:
        criterion = self._validate_target(request)
        if self.repository.find(
            request.student_id, request.course_id, request.criterion_id
        ) is not None:
            raise AlreadyExistsError("Оценка уже существует; используйте edit")
        mark = self.repository.save(
            Mark.create(request.student_id, request.course_id, criterion, request.value)
        )
        return MarkResult.model_validate(mark)

    @route("get")
    def get_mark(self, request: GetMark) -> MarkResult:
        mark = self.repository.get(
            (request.student_id, request.course_id, request.criterion_id)
        )
        return MarkResult.model_validate(mark)

    @route("list")
    def list_marks(self, request: ListMarks) -> list[MarkResult]:
        marks = self.repository.list(limit=request.limit, offset=request.offset)
        return [MarkResult.model_validate(mark) for mark in marks]

    @route("edit")
    def edit_mark(self, request: EditMark) -> MarkResult:
        mark = self.repository.get(
            (request.student_id, request.course_id, request.criterion_id)
        )
        criterion = self._validate_target(request)
        mark.set_score(request.value, criterion)
        return MarkResult.model_validate(self.repository.save(mark))

    @route("delete")
    def delete_mark(self, request: DeleteMark) -> MarkResult:
        mark = self.repository.get(
            (request.student_id, request.course_id, request.criterion_id)
        )
        result = MarkResult.model_validate(mark)
        self.repository.delete(mark)
        return result

    @route("get-student")
    def get_student_marks(self, request: GetStudentMarks) -> list[MarkResult]:
        self.repository.get_student(request.student_id)
        self.repository.get_course(request.course_id)
        self.repository.get_enrollment(request.student_id, request.course_id)
        return [
            MarkResult.model_validate(mark)
            for mark in self.repository.get_student_marks(request.student_id, request.course_id)
        ]

    def _validate_target(self, request: AddMark | EditMark) -> Criterion:
        self.repository.get_student(request.student_id)
        self.repository.get_course(request.course_id)
        criterion = self.repository.get_criterion(request.criterion_id)
        if self.repository.find_enrollment(request.student_id, request.course_id) is None:
            raise RuleViolationError("Студент не зачислен на этот курс")
        if self.repository.find_course_criterion(request.course_id, request.criterion_id) is None:
            raise RuleViolationError("Критерий не входит в рубрикатор курса")
        return criterion
