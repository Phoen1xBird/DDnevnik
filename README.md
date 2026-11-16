# DigitalDnevnik

`ddnevnik` — консольное приложение для учёта студентов, курсов, критериев оценивания и оценок. Оно рассчитывает итог студента по курсу и выгружает ведомость всего курса в CSV. Данные хранятся локально в SQLite.

## Установка

Требуется Python 3.10 или новее. Команды установки выполняются из корневого каталога проекта, где находится `pyproject.toml`.

### macOS и Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
ddnevnik --help
```

При следующем открытии терминала достаточно снова активировать окружение:

```bash
source .venv/bin/activate
```

### Windows, PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\ddnevnik.exe --help
```

В примерах ниже используется команда `ddnevnik`. Если окружение не активировано, на Windows можно вызывать её полным путём `.\.venv\Scripts\ddnevnik.exe`.

`pip install -e .` устанавливает приложение и зависимости из `pyproject.toml`. Режим `-e` позволяет запускать изменённый Python-код без переустановки пакета. После изменения зависимостей или точки входа команду установки нужно повторить.

После установки приложение также можно запускать как Python-модуль:

```bash
python -m ddnevnik --help
```


## Запуск и выбор базы

Путь к базе передавать необязательно:

```bash
ddnevnik students list
```

По умолчанию используется папка данных текущего пользователя:

| Система | Путь по умолчанию |
| --- | --- |
| macOS | `~/Library/Application Support/ddnevnik/ddnevnik.sqlite3` |
| Linux | `~/.local/share/ddnevnik/ddnevnik.sqlite3` |
| Windows | `%LOCALAPPDATA%\ddnevnik\ddnevnik.sqlite3` |

Папка выбирается библиотекой [platformdirs](https://platformdirs.readthedocs.io/en/latest/platforms.html). В Linux она может отличаться, если задана переменная `XDG_DATA_HOME`. Файл базы, папки для него и таблицы создаются автоматически при первой команде работы с данными.

Для отдельной базы укажите `--db` **перед названием группы команд**:

```bash
ddnevnik --db ./demo.sqlite3 students list
```

Относительные пути отсчитываются от текущего рабочего каталога. Чтобы продолжать работу с выбранной базой, указывайте тот же `--db` в последующих командах. Без этой опции приложение вернётся к базе по умолчанию.

Справка доступна для приложения, группы и конкретной команды:

```bash
ddnevnik --help
ddnevnik students --help
ddnevnik courses add-criterion --help
```

## Сквозной пример

Сценарий рассчитан на новый файл `demo.sqlite3`. В пустой базе первые студент и курс получают ID `1`, а два критерия — ID `1` и `2`. Если в выбранной базе уже есть данные, используйте идентификаторы из ответов команд `add`.

### 1. Создать студента, курс и критерии

```bash
ddnevnik --db ./demo.sqlite3 students add "Иван Петров"
ddnevnik --db ./demo.sqlite3 courses add "Python"
ddnevnik --db ./demo.sqlite3 criteria add "Домашняя работа" 10
ddnevnik --db ./demo.sqlite3 criteria add "Экзамен" 20
```

Команды выводят JSON с созданной записью. Например, создание студента вернёт:

```json
{
  "id": 1,
  "name": "Иван Петров"
}
```

### 2. Зачислить студента и настроить рубрикатор курса

```bash
ddnevnik --db ./demo.sqlite3 courses add-student 1 1
ddnevnik --db ./demo.sqlite3 courses add-criterion 1 1 --weight 1
ddnevnik --db ./demo.sqlite3 courses add-criterion 1 2 --weight 3
```

У `courses add-student` порядок аргументов — **ID курса, ID студента**. У `courses add-criterion` — **ID курса, ID критерия**, затем обязательная опция `--weight`.

Максимальный балл задаётся в общем справочнике критериев и одинаков на всех курсах, использующих критерий. Вес назначается отдельно для каждого курса. Веса должны быть положительными; их сумма не обязана равняться единице.

### 3. Выставить оценки

```bash
ddnevnik --db ./demo.sqlite3 marks add 1 1 1 8
ddnevnik --db ./demo.sqlite3 marks add 1 1 2 18
```

Порядок аргументов у `marks add` — **ID студента, ID курса, ID критерия, балл**. Здесь за домашнюю работу выставлено 8 из 10, за экзамен — 18 из 20.

### 4. Получить ведомость курса и выгрузить CSV

```bash
ddnevnik --db ./demo.sqlite3 results course 1 --export ./total.csv
```

Команда принимает только **ID курса** и возвращает ведомость всех зачисленных студентов:

```json
{
  "columns": ["id", "student_name", "Домашняя работа (max 10)", "Экзамен (max 20)", "total"],
  "rows": [
    {
      "id": 1,
      "student_name": "Иван Петров",
      "Домашняя работа (max 10)": 8,
      "Экзамен (max 20)": 18,
      "total": 87.5
    }
  ]
}
```

В CSV будет по одной строке на каждого студента курса. Порядок столбцов: `id`, `student_name`, критерии в порядке их ID, `total`. Название столбца критерия имеет вид `название (max N)`, где `N` — максимальный балл. Если у критериев совпадают и название, и максимум, к таким столбцам добавляется `[id идентификатор]`, чтобы оценки не смешивались.

```csv
id,student_name,Домашняя работа (max 10),Экзамен (max 20),total
1,Иван Петров,8,18,87.5
```

`total` — итог в процентах. Невыставленные оценки показаны как `0`. Студент без оценок тоже входит в ведомость. Если студентов нет, `rows` будет пустым, а CSV будет содержать только заголовок. Если у курса нет критериев, останутся столбцы `id`, `student_name`, `total`; итог будет `null` в JSON и пустой ячейкой в CSV.

Опция `--export` необязательна. CSV записывается в UTF-8 с BOM; родительские папки создаются автоматически. Существующий файл с указанным именем перезаписывается.

### 5. Посмотреть все оценки и итоги студента

```bash
ddnevnik --db ./demo.sqlite3 students marks 1
ddnevnik --db ./demo.sqlite3 results student 1
```

`students marks` возвращает все оценки студента по всем курсам. `results student` возвращает список итогов по каждому курсу, на который студент зачислен. У этих команд нет лимита в 100 записей.

### 6. Исправить или отменить оценку

```bash
ddnevnik --db ./demo.sqlite3 marks edit 1 1 1 10
ddnevnik --db ./demo.sqlite3 results course 1
```

После исправления домашней работы на 10 баллов итог составит `92.5`.

```bash
ddnevnik --db ./demo.sqlite3 marks delete 1 1 2
ddnevnik --db ./demo.sqlite3 results course 1
```

После отмены оценки за экзамен в строке студента будет `0` за экзамен и итог `25.0`. Заполненность 1 из 2 можно посмотреть через `results student 1`. Ранее выгруженный CSV не обновляется автоматически; для новой выгрузки повторите команду с `--export`.

## Как рассчитывается итог

Способ выбирается опцией `--strategy weighted|points` у команд результатов. По умолчанию используется `weighted`.

```text
Итог (%) = 100 × Σ(вес × балл / максимум) / Σ(весов)
```

Для исходного примера:

```text
100 × (1 × 8/10 + 3 × 18/20) / (1 + 3) = 87.5
```

- Невыставленная оценка считается нулём. Вес такого критерия остаётся в знаменателе.
- В результатах `results student` поле `completed_criteria` — количество критериев с выставленной оценкой. Выставленный балл `0` тоже считается заполненной оценкой.
- Поле `total_criteria` в результатах `results student` — количество критериев в рубрикаторе курса.
- Если у курса нет критериев, `total` в ведомости и `total_score` в итогах студента равны `null`.
- Итог вычисляется по текущим данным, округляется через `round(..., 2)` и отдельно в БД не хранится.

Для `points` используется формула `100 × Σ(баллов) / Σ(максимумов)`. В примере выше результат равен `86.67`. Пропуски считаются нулями, при пустом рубрикаторе итог равен `null`.

```bash
ddnevnik --db ./demo.sqlite3 results course 1 --strategy points --export ./points.csv
ddnevnik --db ./demo.sqlite3 results student 1 --strategy points
ddnevnik --db ./demo.sqlite3 results student-course 1 1 --strategy weighted
```

Расчёт выполняет `ResultsAPI`.

## Использование ResultsAPI из Python

После установки пакета команды расчёта можно вызывать через `CommandBuilder`. Пример ниже создаёт SQLite в памяти, студента, курс и оценки, затем сравнивает результаты двух стратегий.

| Маршрут | Входная схема | Обязательные поля `request` | Результат |
| --- | --- | --- | --- |
| `results/course` | `GetCourseResults` | `course_id` | `CourseTotalsResult` — ведомость всех зачисленных студентов с баллами по критериям и итоговым процентом |
| `results/student` | `GetStudentResults` | `student_id` | `list[TotalResult]` — итоги и заполненность по всем курсам студента |
| `results/student-course` | `GetStudentCourseResults` | `student_id`, `course_id` | `TotalResult` — итог и заполненность по одному курсу |

В билдер передаются имя API `results` и имя маршрута `course`, `student` или `student-course` отдельными аргументами. У всех схем есть необязательный `strategy` со значениями `weighted` и `points`, по умолчанию — `weighted`. Неизвестное значение приводит к `InvalidParametersError` при валидации запроса. [Схемы запросов и ответов](src/ddnevnik/schemas/results.py).

```python
from ddnevnik.command_builder import CommandBuilder
from ddnevnik.workers import DatabaseWorker

database = DatabaseWorker(":memory:")
database.create_tables()
try:
    builder = CommandBuilder(database)
    student, course, homework, exam = (
        builder
        .add_command("students", "add", request={"name": "Иван"})
        .add_command("courses", "add", request={"name": "Python"})
        .add_command("criteria", "add", request={"name": "ДЗ", "max_score": 10})
        .add_command("criteria", "add", request={"name": "Экзамен", "max_score": 20})
        .execute()
    )
    builder.add_command("courses", "add-student", request={
        "course_id": course.id, "student_id": student.id,
    })
    for criterion, weight, value in [(homework, 1, 8), (exam, 3, 18)]:
        builder.add_command("courses", "add-criterion", request={
            "course_id": course.id, "criterion_id": criterion.id, "weight": weight,
        })
        builder.add_command("marks", "add", request={
            "student_id": student.id, "course_id": course.id,
            "criterion_id": criterion.id, "value": value,
        })
    builder.execute()

    reports = (
        builder
        .add_command("results", "course", request={
            "course_id": course.id, "strategy": "weighted",
        })
        .add_command("results", "course", request={
            "course_id": course.id, "strategy": "points",
        })
        .add_command("results", "course", request={"course_id": course.id})
        .execute()
    )
    print([report.rows[0]["total"] for report in reports])
    # [87.5, 86.67, 87.5]
finally:
    database.close()
```

## Справочник команд

В таблицах ниже команды используют базу по умолчанию. Для другого файла добавьте `--db ПУТЬ` сразу после `ddnevnik`. Значения в угловых скобках нужно заменить своими; сами скобки вводить не нужно. Имена с пробелами заключайте в кавычки.

### Студенты

| Команда | Действие |
| --- | --- |
| `ddnevnik students add "<имя>"` | Создать студента |
| `ddnevnik students get <student_id>` | Получить студента |
| `ddnevnik students list` | Список студентов |
| `ddnevnik students edit <student_id> "<новое имя>"` | Переименовать студента |
| `ddnevnik students delete <student_id>` | Удалить студента |
| `ddnevnik students add-course <student_id> <course_id>` | Зачислить студента на курс |
| `ddnevnik students courses <student_id>` | Список курсов студента |
| `ddnevnik students marks <student_id>` | Все оценки студента |

### Курсы

| Команда | Действие |
| --- | --- |
| `ddnevnik courses add "<название>"` | Создать курс |
| `ddnevnik courses get <course_id>` | Получить курс |
| `ddnevnik courses list` | Список курсов |
| `ddnevnik courses edit <course_id> "<новое название>"` | Переименовать курс |
| `ddnevnik courses delete <course_id>` | Удалить курс |
| `ddnevnik courses add-student <course_id> <student_id>` | Зачислить студента |
| `ddnevnik courses add-criterion <course_id> <criterion_id> --weight <вес>` | Добавить критерий в рубрикатор |
| `ddnevnik courses students <course_id>` | Список студентов курса |
| `ddnevnik courses criteria <course_id>` | Рубрикатор с максимумами и весами |

### Критерии

| Команда | Действие |
| --- | --- |
| `ddnevnik criteria add "<название>" <максимум>` | Создать критерий |
| `ddnevnik criteria get <criterion_id>` | Получить критерий |
| `ddnevnik criteria list` | Список критериев |
| `ddnevnik criteria edit <criterion_id> --name "<название>"` | Изменить название |
| `ddnevnik criteria edit <criterion_id> --max-score <максимум>` | Изменить максимальный балл |
| `ddnevnik criteria delete <criterion_id>` | Удалить критерий |

При изменении можно передать `--name` и `--max-score` вместе. Нужно указать хотя бы одну из этих опций.

### Оценки

| Команда | Действие |
| --- | --- |
| `ddnevnik marks add <student_id> <course_id> <criterion_id> <балл>` | Выставить новую оценку |
| `ddnevnik marks get <student_id> <course_id> <criterion_id>` | Получить оценку |
| `ddnevnik marks list` | Список всех оценок |
| `ddnevnik marks edit <student_id> <course_id> <criterion_id> <балл>` | Исправить оценку |
| `ddnevnik marks delete <student_id> <course_id> <criterion_id>` | Отменить оценку |
| `ddnevnik marks student <student_id> <course_id>` | Оценки студента по одному курсу |

### Результаты

| Команда | Действие |
| --- | --- |
| `ddnevnik results course <course_id>` | Ведомость всех студентов курса |
| `ddnevnik results student <student_id>` | Итоги по всем курсам студента |
| `ddnevnik results student-course <student_id> <course_id>` | Итог студента по одному курсу |

Все команды группы принимают `--strategy weighted` или `--strategy points`. Для `results course` доступен `--export <путь.csv>`.

### Размер списков

Команды `students list`, `courses list`, `criteria list`, `marks list`, `students courses` и `courses students` поддерживают `--limit` и `--offset`. По умолчанию `limit=100`, `offset=0`.

```bash
ddnevnik students list --limit 10 --offset 20
ddnevnik courses students 1 --limit 25
```

Команда `courses criteria` возвращает весь рубрикатор курса. Команды `results student`, `students marks` и `marks student` также возвращают полные списки.
