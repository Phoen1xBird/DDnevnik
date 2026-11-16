import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, TypeVar

from platformdirs import user_data_path
from sqlalchemy import MetaData, create_engine, event
from sqlalchemy.engine import URL, Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from ddnevnik.errors import (
    AlreadyExistsError,
    NotFoundError,
    RuleViolationError,
    StorageError,
)
from ddnevnik.models import Base

ModelT = TypeVar("ModelT", bound=Base)


def _enable_foreign_keys(connection: sqlite3.Connection, _: Any) -> None:
    cursor = connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
    finally:
        cursor.close()


class DatabaseWorker:

    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path is None:
            db_path = user_data_path("ddnevnik", appauthor=False) / "ddnevnik.sqlite3"

        if str(db_path) == ":memory:":
            self.db_path = None
            database = ":memory:"
        else:
            self.db_path = Path(db_path).expanduser().resolve()
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            database = str(self.db_path)

        self.engine: Engine = create_engine(
            URL.create("sqlite+pysqlite", database=database)
        )
        event.listen(self.engine, "connect", _enable_foreign_keys)
        self._session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    def create_tables(self, metadata: MetaData | None = None) -> None:
        if metadata is None:
            metadata = Base.metadata
        metadata.create_all(self.engine)
        if self.engine.dialect.name == "sqlite":
            with self.engine.begin() as connection:
                for name in (
                    "marks_max_score_insert",
                    "marks_max_score_update",
                    "criteria_max_score_update",
                ):
                    connection.exec_driver_sql(f"DROP TRIGGER IF EXISTS {name}")

    @contextmanager
    def session(self) -> Iterator[Session]:
        try:
            with self._session_factory.begin() as session:
                yield session
        except IntegrityError as error:
            message = str(error.orig)
            if "UNIQUE constraint failed" in message:
                raise AlreadyExistsError("Такая запись уже существует") from None
            if "FOREIGN KEY constraint failed" in message:
                raise RuleViolationError("Указанная связанная запись не существует") from None
            raise StorageError(f"Не удалось сохранить изменения: {message}") from None

    @staticmethod
    def require(
        session: Session, model: type[ModelT], key: int | tuple[int, ...]
    ) -> ModelT:
        item = session.get(model, key)
        if item is None:
            names = {
                "students": "студент",
                "courses": "курс",
                "criteria": "критерий",
                "enrollments": "зачисление",
                "course_criteria": "критерий курса",
                "marks": "оценка",
            }
            name = names.get(model.__tablename__, "запись")
            raise NotFoundError(f"Запись не найдена: {name}, ключ {key}")
        return item

    def close(self) -> None:
        self.engine.dispose()
