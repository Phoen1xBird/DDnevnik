from pathlib import Path

import typer

from .apps.courses import app as courses
from .apps.criteria import app as criteria
from .apps.marks import app as marks
from .apps.results import app as results
from .apps.students import app as students

app = typer.Typer(no_args_is_help=True, help="Дневник преподавательской оценки студентов.")
app.add_typer(students, name="students")
app.add_typer(courses, name="courses")
app.add_typer(criteria, name="criteria")
app.add_typer(marks, name="marks")
app.add_typer(results, name="results")


@app.callback()
def main(
    ctx: typer.Context,
    db: Path | None = typer.Option(None, "--db", help="Путь к файлу SQLite."),
) -> None:
    ctx.obj = db
