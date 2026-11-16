import typer

from .common import _run, _show

app = typer.Typer(no_args_is_help=True, help="Выставление и исправление оценок.")


@app.command("add", help="Выставить новую оценку.")
def mark_add(
    ctx: typer.Context, student_id: int, course_id: int, criterion_id: int, value: int
) -> None:
    _show(
        _run(
            ctx, "marks", "add",
            student_id=student_id,
            course_id=course_id,
            criterion_id=criterion_id,
            value=value,
        )
    )


@app.command("get", help="Получить оценку по студенту, курсу и критерию.")
def mark_get(ctx: typer.Context, student_id: int, course_id: int, criterion_id: int) -> None:
    _show(
        _run(
            ctx, "marks", "get",
            student_id=student_id,
            course_id=course_id,
            criterion_id=criterion_id,
        )
    )


@app.command("list", help="Показать все выставленные оценки.")
def mark_list(ctx: typer.Context, limit: int = 100, offset: int = 0) -> None:
    _show(_run(ctx, "marks", "list", limit=limit, offset=offset))


@app.command("edit", help="Исправить существующую оценку.")
def mark_edit(
    ctx: typer.Context, student_id: int, course_id: int, criterion_id: int, value: int
) -> None:
    _show(
        _run(
            ctx, "marks", "edit",
            student_id=student_id,
            course_id=course_id,
            criterion_id=criterion_id,
            value=value,
        )
    )


@app.command("delete", help="Отменить оценку.")
def mark_delete(ctx: typer.Context, student_id: int, course_id: int, criterion_id: int) -> None:
    _show(
        _run(
            ctx, "marks", "delete",
            student_id=student_id,
            course_id=course_id,
            criterion_id=criterion_id,
        )
    )


@app.command("student", help="Показать оценки студента по курсу.")
def mark_student(ctx: typer.Context, student_id: int, course_id: int) -> None:
    _show(_run(ctx, "marks", "get-student", student_id=student_id, course_id=course_id))
