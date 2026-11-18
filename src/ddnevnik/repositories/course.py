from sqlalchemy import select
from sqlalchemy.orm import Session

from ddnevnik.models import Course, CourseCriterion, Criterion, Enrollment, Mark, Student
from ddnevnik.schemas.results import CourseCriterionResult


from ddnevnik.schemas.repositories import EntityKey
from ddnevnik.workers.database import DatabaseWorker


class SQLAlchemyCourseRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, key: EntityKey) -> Course:
        return DatabaseWorker.require(self._session, Course, key)

    def save(self, entity: Course) -> Course:
        self._session.add(entity)
        self._session.flush()
        return entity

    def delete(self, entity: Course) -> None:
        self._session.delete(entity)

    def get_student(self, student_id: int) -> Student:
        return DatabaseWorker.require(self._session, Student, student_id)

    def get_criterion(self, criterion_id: int) -> Criterion:
        return DatabaseWorker.require(self._session, Criterion, criterion_id)

    def get_enrollment(self, student_id: int, course_id: int) -> Enrollment:
        return DatabaseWorker.require(self._session, Enrollment, (student_id, course_id))

    def find_enrollment(self, student_id: int, course_id: int) -> Enrollment | None:
        return self._session.get(Enrollment, (student_id, course_id))

    def add_enrollment(self, student_id: int, course_id: int) -> Enrollment:
        enrollment = Enrollment(student_id=student_id, course_id=course_id)
        self._session.add(enrollment)
        self._session.flush()
        return enrollment

    def find_criterion(self, course_id: int, criterion_id: int) -> CourseCriterion | None:
        return self._session.get(CourseCriterion, (course_id, criterion_id))

    def add_criterion(
        self, course_id: int, criterion_id: int, weight: float
    ) -> CourseCriterion:
        link = CourseCriterion(
            course_id=course_id, criterion_id=criterion_id, weight=weight
        )
        self._session.add(link)
        self._session.flush()
        return link

    def get_students(
        self, course_id: int, *, limit: int | None = 100, offset: int = 0
    ) -> list[Student]:
        query = (
            select(Student)
            .join(Enrollment, Enrollment.student_id == Student.id)
            .where(Enrollment.course_id == course_id)
            .order_by(Student.id)
            .offset(offset)
            .limit(limit)
        )
        return list(self._session.scalars(query))

    def get_rubric(self, course_id: int) -> list[CourseCriterionResult]:
        query = (
            select(CourseCriterion, Criterion)
            .join(Criterion, Criterion.id == CourseCriterion.criterion_id)
            .where(CourseCriterion.course_id == course_id)
            .order_by(CourseCriterion.criterion_id)
        )
        return [
            CourseCriterionResult(
                course_id=link.course_id,
                criterion_id=link.criterion_id,
                name=criterion.name,
                max_score=criterion.max_score,
                weight=link.weight,
            )
            for link, criterion in self._session.execute(query)
        ]

    def get_marks(self, course_id: int, *, student_id: int | None = None) -> list[Mark]:
        query = (
            select(Mark)
            .where(Mark.course_id == course_id)
            .order_by(Mark.student_id, Mark.criterion_id)
        )
        if student_id is not None:
            query = query.where(Mark.student_id == student_id)
        return list(self._session.scalars(query))

    def list(self, *, limit: int = 100, offset: int = 0) -> list[Course]:
        query = (
            select(Course)
            .order_by(*Course.__table__.primary_key.columns)
            .offset(offset)
            .limit(limit)
        )
        return list(self._session.scalars(query))
