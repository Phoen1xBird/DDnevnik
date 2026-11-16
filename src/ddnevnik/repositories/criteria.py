from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ddnevnik.models import Criterion, Mark


from ddnevnik.schemas.repositories import EntityKey
from ddnevnik.workers.database import DatabaseWorker


class SQLAlchemyCriteriaRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, key: EntityKey) -> Criterion:
        return DatabaseWorker.require(self._session, Criterion, key)

    def save(self, entity: Criterion) -> Criterion:
        self._session.add(entity)
        self._session.flush()
        return entity

    def delete(self, entity: Criterion) -> None:
        self._session.delete(entity)

    def get_highest_mark(self, criterion_id: int) -> int | None:
        return self._session.scalar(
            select(func.max(Mark.value)).where(Mark.criterion_id == criterion_id)
        )

    def list(self, *, limit: int = 100, offset: int = 0) -> list[Criterion]:
        query = (
            select(Criterion)
            .order_by(*Criterion.__table__.primary_key.columns)
            .offset(offset)
            .limit(limit)
        )
        return list(self._session.scalars(query))
