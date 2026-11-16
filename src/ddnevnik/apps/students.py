import typer

from .common import _run, _show

app = typer.Typer(no_args_is_help=True, help="Студенты и их курсы.")


@app.command("add", help="Создать студента.")
def student_add(ctx: typer.Context, name: str) -> None:
    _show(_run(ctx, "students", "add", name=name))


@app.command("get", help="Получить студента по ID.")
def student_get(ctx: typer.Context, student_id: int) -> None:
    _show(_run(ctx, "students", "get", student_id=student_id))


@app.command("list", help="Показать список студентов.")
def student_list(
    ctx: typer.Context, limit: int = 100, offset: int = 0
) -> None:
    _show(_run(ctx, "students", "list", limit=limit, offset=offset))


@app.command("edit", help="Изменить имя студента.")
def student_edit(ctx: typer.Context, student_id: int, new_name: str) -> None:
    _show(_run(ctx, "students", "edit", student_id=student_id, new_name=new_name))


@app.command("delete", help="Удалить студента, его зачисления и оценки.")
def student_delete(ctx: typer.Context, student_id: int) -> None:
    _show(_run(ctx, "students", "delete", student_id=student_id))


@app.command("add-course", help="Зачислить студента на курс.")
def student_add_course(ctx: typer.Context, student_id: int, course_id: int) -> None:
    _show(_run(ctx, "students", "add-course", student_id=student_id, course_id=course_id))


@app.command("courses", help="Показать курсы студента.")
def student_courses(
    ctx: typer.Context, student_id: int, limit: int = 100, offset: int = 0
) -> None:
    _show(
        _run(
            ctx, "students", "get-courses",
            student_id=student_id,
            limit=limit,
            offset=offset,
        )
    )


@app.command("marks", help="Показать все оценки студента по всем курсам.")
def student_marks(ctx: typer.Context, student_id: int) -> None:
    _show(_run(ctx, "students", "get-marks", student_id=student_id))
