from sqlalchemy import select
from sqlalchemy.orm import Session

from ddnevnik.models import Course, CourseCriterion, Criterion, Enrollment, Mark, Student
from ddnevnik.schemas.results import CourseCriterionResult


from ddnevnik.schemas.repositories import EntityKey
from ddnevnik.workers.database import DatabaseWorker


class SQLAlchemyStudentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, key: EntityKey) -> Student:
        return DatabaseWorker.require(self._session, Student, key)

    def save(self, entity: Student) -> Student:
        self._session.add(entity)
        self._session.flush()
        return entity

    def delete(self, entity: Student) -> None:
        self._session.delete(entity)

    def get_course(self, course_id: int) -> Course:
        return DatabaseWorker.require(self._session, Course, course_id)

    def find_enrollment(self, student_id: int, course_id: int) -> Enrollment | None:
        return self._session.get(Enrollment, (student_id, course_id))

    def add_enrollment(self, student_id: int, course_id: int) -> Enrollment:
        enrollment = Enrollment(student_id=student_id, course_id=course_id)
        self._session.add(enrollment)
        self._session.flush()
        return enrollment

    def get_courses(
        self, student_id: int, *, limit: int | None = 100, offset: int = 0
    ) -> list[Course]:
        query = (
            select(Course)
            .join(Enrollment, Enrollment.course_id == Course.id)
            .where(Enrollment.student_id == student_id)
            .order_by(Course.id)
            .offset(offset)
            .limit(limit)
        )
        return list(self._session.scalars(query))

    def get_rubrics(self, student_id: int) -> list[CourseCriterionResult]:
        query = (
            select(CourseCriterion, Criterion)
            .join(Criterion, Criterion.id == CourseCriterion.criterion_id)
            .join(Enrollment, Enrollment.course_id == CourseCriterion.course_id)
            .where(Enrollment.student_id == student_id)
            .order_by(CourseCriterion.course_id, CourseCriterion.criterion_id)
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

    def get_marks(self, student_id: int) -> list[Mark]:
        query = (
            select(Mark)
            .where(Mark.student_id == student_id)
            .order_by(Mark.course_id, Mark.criterion_id)
        )
        return list(self._session.scalars(query))

    def list(self, *, limit: int = 100, offset: int = 0) -> list[Student]:
        query = (
            select(Student)
            .order_by(*Student.__table__.primary_key.columns)
            .offset(offset)
            .limit(limit)
        )
        return list(self._session.scalars(query))
