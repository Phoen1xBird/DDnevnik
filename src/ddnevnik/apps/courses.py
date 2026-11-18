import typer

from .common import _run, _show

app = typer.Typer(no_args_is_help=True, help="Курсы и рубрикатор.")


@app.command("add", help="Создать курс.")
def course_add(ctx: typer.Context, name: str) -> None:
    _show(_run(ctx, "courses", "add", name=name))


@app.command("get", help="Получить курс по ID.")
def course_get(ctx: typer.Context, course_id: int) -> None:
    _show(_run(ctx, "courses", "get", course_id=course_id))


@app.command("list", help="Показать список курсов.")
def course_list(ctx: typer.Context, limit: int = 100, offset: int = 0) -> None:
    _show(_run(ctx, "courses", "list", limit=limit, offset=offset))


@app.command("edit", help="Изменить имя курса.")
def course_edit(ctx: typer.Context, course_id: int, new_name: str) -> None:
    _show(_run(ctx, "courses", "edit", course_id=course_id, new_name=new_name))


@app.command("delete", help="Удалить курс с зачислениями, рубрикатором и оценками.")
def course_delete(ctx: typer.Context, course_id: int) -> None:
    _show(_run(ctx, "courses", "delete", course_id=course_id))


@app.command("add-student", help="Зачислить студента на курс.")
def course_add_student(ctx: typer.Context, course_id: int, student_id: int) -> None:
    _show(_run(ctx, "courses", "add-student", course_id=course_id, student_id=student_id))


@app.command("add-criterion", help="Добавить критерий в курс и назначить вес.")
def course_add_criterion(
    ctx: typer.Context,
    course_id: int,
    criterion_id: int,
    weight: float = typer.Option(..., "--weight", help="Положительный вес критерия."),
) -> None:
    _show(
        _run(
            ctx, "courses", "add-criterion",
            course_id=course_id,
            criterion_id=criterion_id,
            weight=weight,
        )
    )


@app.command("students", help="Показать студентов курса.")
def course_students(
    ctx: typer.Context, course_id: int, limit: int = 100, offset: int = 0
) -> None:
    _show(_run(ctx, "courses", "get-students", course_id=course_id, limit=limit, offset=offset))


@app.command("criteria", help="Показать критерии курса с максимумами и весами.")
def course_criteria(ctx: typer.Context, course_id: int) -> None:
    _show(_run(ctx, "courses", "get-criteria", course_id=course_id))
