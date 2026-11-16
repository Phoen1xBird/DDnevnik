import typer

from .common import _run, _show

app = typer.Typer(no_args_is_help=True, help="Общий справочник критериев.")


@app.command("add", help="Создать критерий с максимальным баллом.")
def criterion_add(ctx: typer.Context, name: str, max_score: int) -> None:
    _show(_run(ctx, "criteria", "add", name=name, max_score=max_score))


@app.command("get", help="Получить критерий по ID.")
def criterion_get(ctx: typer.Context, criterion_id: int) -> None:
    _show(_run(ctx, "criteria", "get", criterion_id=criterion_id))


@app.command("list", help="Показать справочник критериев.")
def criterion_list(ctx: typer.Context, limit: int = 100, offset: int = 0) -> None:
    _show(_run(ctx, "criteria", "list", limit=limit, offset=offset))


@app.command("edit", help="Изменить имя или максимум критерия.")
def criterion_edit(
    ctx: typer.Context,
    criterion_id: int,
    name: str | None = typer.Option(None, "--name"),
    max_score: int | None = typer.Option(None, "--max-score"),
) -> None:
    _show(
        _run(
            ctx, "criteria", "edit",
            criterion_id=criterion_id,
            new_name=name,
            max_score=max_score,
        )
    )


@app.command("delete", help="Удалить критерий из всех курсов вместе с его оценками.")
def criterion_delete(ctx: typer.Context, criterion_id: int) -> None:
    _show(_run(ctx, "criteria", "delete", criterion_id=criterion_id))
