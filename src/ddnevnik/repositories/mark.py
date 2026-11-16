from sqlalchemy import select
from sqlalchemy.orm import Session

from ddnevnik.models import Course, CourseCriterion, Criterion, Enrollment, Mark, Student


from ddnevnik.schemas.repositories import EntityKey
from ddnevnik.workers.database import DatabaseWorker


class SQLAlchemyMarkRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, key: EntityKey) -> Mark:
        return DatabaseWorker.require(self._session, Mark, key)

    def save(self, entity: Mark) -> Mark:
        self._session.add(entity)
        self._session.flush()
        return entity

    def delete(self, entity: Mark) -> None:
        self._session.delete(entity)

    def get_student(self, student_id: int) -> Student:
        return DatabaseWorker.require(self._session, Student, student_id)

    def get_course(self, course_id: int) -> Course:
        return DatabaseWorker.require(self._session, Course, course_id)

    def get_criterion(self, criterion_id: int) -> Criterion:
        return DatabaseWorker.require(self._session, Criterion, criterion_id)

    def get_enrollment(self, student_id: int, course_id: int) -> Enrollment:
        return DatabaseWorker.require(self._session, Enrollment, (student_id, course_id))

    def find(self, student_id: int, course_id: int, criterion_id: int) -> Mark | None:
        return self._session.get(Mark, (student_id, course_id, criterion_id))

    def find_enrollment(self, student_id: int, course_id: int) -> Enrollment | None:
        return self._session.get(Enrollment, (student_id, course_id))

    def find_course_criterion(
        self, course_id: int, criterion_id: int
    ) -> CourseCriterion | None:
        return self._session.get(CourseCriterion, (course_id, criterion_id))

    def get_student_marks(self, student_id: int, course_id: int) -> list[Mark]:
        query = (
            select(Mark)
            .where(Mark.student_id == student_id, Mark.course_id == course_id)
            .order_by(Mark.criterion_id)
        )
        return list(self._session.scalars(query))

    def list(self, *, limit: int = 100, offset: int = 0) -> list[Mark]:
        query = (
            select(Mark)
            .order_by(*Mark.__table__.primary_key.columns)
            .offset(offset)
            .limit(limit)
        )
        return list(self._session.scalars(query))
