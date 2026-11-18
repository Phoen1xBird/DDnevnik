import json
from typing import Any

import typer
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from ddnevnik.command_builder import CommandBuilder
from ddnevnik.errors import (
    AlreadyExistsError,
    IncompleteCommandError,
    InvalidParametersError,
    NotFoundError,
    RuleViolationError,
    StorageError,
    UnknownAPIError,
    UnknownRouteError,
)
from ddnevnik.workers import DatabaseWorker


def _run(ctx: typer.Context, api_name: str, route_name: str, **data: Any) -> Any:
    database = None
    try:
        database = DatabaseWorker(ctx.find_root().obj)
        ctx.find_root().meta["db_path"] = database.db_path
        database.create_tables()
        return (
            CommandBuilder(database)
            .add_command(api_name, route_name, request=data)
            .execute()[0]
        )
    except (
        AlreadyExistsError,
        IncompleteCommandError,
        InvalidParametersError,
        NotFoundError,
        RuleViolationError,
        StorageError,
        UnknownAPIError,
        UnknownRouteError,
        SQLAlchemyError,
        OSError,
    ) as error:
        typer.echo(f"Ошибка: {error}", err=True)
        raise typer.Exit(code=1) from None
    finally:
        if database is not None:
            database.close()


def _show(result: Any) -> None:
    if isinstance(result, BaseModel):
        data = result.model_dump(mode="json")
    else:
        data = [item.model_dump(mode="json") for item in result]
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2))
