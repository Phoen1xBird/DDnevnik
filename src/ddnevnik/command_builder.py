from typing import Any

from sqlalchemy.orm import Session

from ddnevnik.core import CourseAPI, CriteriaAPI, MarkAPI, ResultsAPI, StudentAPI
from ddnevnik.errors import IncompleteCommandError, UnknownAPIError
from ddnevnik.repositories.course import SQLAlchemyCourseRepository
from ddnevnik.repositories.criteria import SQLAlchemyCriteriaRepository
from ddnevnik.repositories.mark import SQLAlchemyMarkRepository
from ddnevnik.repositories.student import SQLAlchemyStudentRepository
from ddnevnik.workers.database import DatabaseWorker


class CommandBuilder:

    def __init__(self, database: DatabaseWorker | None = None) -> None:
        self._database = database
        self._owns_database = database is None
        self._commands: list[tuple[str, str, dict[str, Any]]] = []

    def add_command(
        self,
        api: str,
        router: str,
        *,
        in_place: bool = True,
        **kwargs: Any,
    ) -> "CommandBuilder":
        builder = self if in_place else CommandBuilder(self._database)
        if not in_place:
            builder._commands = self._commands.copy()
        builder._commands.append((api, router, kwargs))
        return builder

    def execute(self) -> list[Any]:
        if not self._commands:
            raise IncompleteCommandError("Не добавлены команды")

        commands, self._commands = self._commands, []
        for api_name, _, _ in commands:
            if api_name not in {"students", "courses", "criteria", "marks", "results"}:
                raise UnknownAPIError(f"Неизвестный API: {api_name!r}")

        if self._database is None:
            self._database = DatabaseWorker()
            self._database.create_tables()
        with self._database.session() as session:
            results = []
            for api_name, router_name, params in commands:
                api = self._create_api(api_name, session)
                results.append(api.execute(router_name, **params))
            return results

    def _create_api(self, name: str, session: Session):
        if name == "students":
            return StudentAPI(SQLAlchemyStudentRepository(session))
        elif name == "courses":
            return CourseAPI(SQLAlchemyCourseRepository(session))
        elif name == "criteria":
            return CriteriaAPI(SQLAlchemyCriteriaRepository(session))
        elif name == "marks":
            return MarkAPI(SQLAlchemyMarkRepository(session))
        elif name == "results":
            return ResultsAPI(
                SQLAlchemyCourseRepository(session), SQLAlchemyStudentRepository(session)
            )
        else:
            raise UnknownAPIError(f"Неизвестный API: {name!r}")

    def close(self) -> None:
        if self._owns_database and self._database is not None:
            self._database.close()
