import csv
from pathlib import Path

import typer

from ddnevnik.schemas.results import TotalMethod

from .common import _run, _show

app = typer.Typer(no_args_is_help=True, help="Итоги студентов и ведомости курсов.")


@app.command("course", help="Показать ведомость всех студентов курса.")
def course_total(
    ctx: typer.Context,
    course_id: int,
    export: Path | None = typer.Option(None, "--export", help="Выгрузить ведомость в CSV."),
    strategy: TotalMethod = typer.Option(
        TotalMethod.WEIGHTED, "--strategy", help="Способ расчёта итогового процента."
    ),
) -> None:
    result = _run(ctx, "results", "course", course_id=course_id, strategy=strategy)
    if export is not None:
        try:
            export.parent.mkdir(parents=True, exist_ok=True)
            with export.open("w", encoding="utf-8-sig", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=result.columns)
                writer.writeheader()
                writer.writerows(result.rows)
        except OSError as error:
            typer.echo(f"Ошибка выгрузки: {error}", err=True)
            raise typer.Exit(code=1) from None
    _show(result)


@app.command("student", help="Показать итоги по всем курсам студента.")
def student_totals(
    ctx: typer.Context,
    student_id: int,
    strategy: TotalMethod = typer.Option(
        TotalMethod.WEIGHTED, "--strategy", help="Способ расчёта итогового процента."
    ),
) -> None:
    _show(_run(ctx, "results", "student", student_id=student_id, strategy=strategy))


@app.command("student-course", help="Показать итог студента по одному курсу.")
def student_course_total(
    ctx: typer.Context,
    student_id: int,
    course_id: int,
    strategy: TotalMethod = typer.Option(
        TotalMethod.WEIGHTED, "--strategy", help="Способ расчёта итогового процента."
    ),
) -> None:
    _show(_run(
        ctx, "results", "student-course",
        student_id=student_id, course_id=course_id, strategy=strategy,
    ))
