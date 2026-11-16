import unittest
from unittest.mock import create_autospec

from ddnevnik.command_builder import CommandBuilder
from ddnevnik.core import StudentAPI
from ddnevnik.errors import (
    AlreadyExistsError,
    IncompleteCommandError,
    InvalidParametersError,
    RuleViolationError,
)
from ddnevnik.models import Mark, MaxScore, Score, Student
from ddnevnik.repositories.mark import SQLAlchemyMarkRepository
from ddnevnik.schemas.repositories import StudentRepository
from ddnevnik.workers import DatabaseWorker


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.database = DatabaseWorker(":memory:")
        self.addCleanup(self.database.close)
        self.database.create_tables()
        self.builder = CommandBuilder(self.database)
        self.student, self.course, self.homework, self.exam = (
            self.builder
            .add_command("students", "add", request={"name": "Иван"})
            .add_command("courses", "add", request={"name": "Python"})
            .add_command("criteria", "add", request={"name": "ДЗ", "max_score": 10})
            .add_command("criteria", "add", request={"name": "Экзамен", "max_score": 20})
            .execute()
        )
        self.builder.add_command(
            "courses", "add-student",
            request={"course_id": self.course.id, "student_id": self.student.id},
        )
        for criterion, weight in [(self.homework, 1), (self.exam, 3)]:
            self.builder.add_command(
                "courses", "add-criterion",
                request={
                    "course_id": self.course.id, "criterion_id": criterion.id, "weight": weight,
                },
            )
        self.builder.execute()
        self.target = {
            "student_id": self.student.id,
            "course_id": self.course.id,
            "criterion_id": self.homework.id,
        }

    def execute(self, api, route, **params):
        return self.builder.add_command(api, route, request=params).execute()[0]

    def total(self):
        return self.execute("results", "student", student_id=self.student.id)[0]

    def test_course_scenario(self):
        self.assertEqual(self.total().total_score, 0)
        exam = self.target | {"criterion_id": self.exam.id}
        _, totals, _, report = (
            self.builder
            .add_command("marks", "add", request=self.target | {"value": 8})
            .add_command("results", "student", request={"student_id": self.student.id})
            .add_command("marks", "add", request=exam | {"value": 18})
            .add_command("results", "course", request={"course_id": self.course.id})
            .execute()
        )
        total = totals[0]
        self.assertEqual(
            (total.total_score, total.completed_criteria, total.total_criteria), (20, 1, 2)
        )

        self.assertEqual(self.total().total_score, 87.5)
        self.assertEqual(
            report.columns, ["id", "student_name", "ДЗ (max 10)", "Экзамен (max 20)", "total"]
        )
        self.assertEqual(report.rows, [{
            "id": self.student.id, "student_name": "Иван",
            "ДЗ (max 10)": 8, "Экзамен (max 20)": 18, "total": 87.5,
        }])

        _, edited, _, deleted = (
            self.builder
            .add_command("marks", "edit", request=self.target | {"value": 10})
            .add_command("results", "student", request={"student_id": self.student.id})
            .add_command("marks", "delete", request=exam)
            .add_command("results", "student", request={"student_id": self.student.id})
            .execute()
        )
        self.assertEqual(edited[0].total_score, 92.5)
        total = deleted[0]
        self.assertEqual((total.total_score, total.completed_criteria), (25, 1))
        with self.assertRaises(IncompleteCommandError):
            self.builder.execute()

    def test_branches_are_independent_and_failed_batch_rolls_back(self):
        original = self.builder.add_command(
            "students", "get", request={"student_id": self.student.id}
        )
        self.assertIs(original, self.builder)
        common = original.add_command(
            "marks", "add", request=self.target | {"value": 8}, in_place=False
        )
        exam = self.target | {"criterion_id": self.exam.id}
        successful = (
            common
            .add_command("marks", "add", request=exam | {"value": 18}, in_place=False)
            .add_command("results", "course", request={"course_id": self.course.id})
        )
        failing = common.add_command(
            "marks", "add", request=exam | {"value": 21}, in_place=False
        )
        self.assertIsNot(common, original)
        self.assertIsNot(successful, failing)

        with self.assertRaises(RuleViolationError):
            failing.execute()

        self.assertEqual([item.name for item in original.execute()], ["Иван"])
        self.assertEqual(self.execute(
            "marks", "get-student", student_id=self.student.id, course_id=self.course.id
        ), [])

        student, homework, exam_mark, report = successful.execute()
        self.assertEqual(student.name, "Иван")
        self.assertEqual((homework.value, exam_mark.value), (8, 18))
        self.assertEqual(report.rows[0]["total"], 87.5)
        self.assertEqual(self.total().total_score, 87.5)

    def test_invalid_commands_preserve_marks(self):
        self.execute("marks", "add", **self.target, value=8)
        outsider = self.execute("criteria", "add", name="Вне рубрикатора", max_score=10)
        student = self.execute("students", "add", name="Не зачислен")
        cases = [
            (RuleViolationError, "marks", "edit", self.target | {"value": 11}),
            (InvalidParametersError, "marks", "edit", self.target | {"value": -1}),
            (AlreadyExistsError, "marks", "add", self.target | {"value": 8}),
            (RuleViolationError, "marks", "add", self.target | {
                "criterion_id": outsider.id, "value": 5,
            }),
            (RuleViolationError, "marks", "add", self.target | {
                "student_id": student.id, "value": 5,
            }),
            (RuleViolationError, "criteria", "edit", {
                "criterion_id": self.homework.id, "max_score": 7,
            }),
            (InvalidParametersError, "marks", "add", self.target),
        ]
        for error, api, route, params in cases:
            with self.subTest(api=api, route=route, params=params):
                with self.assertRaises(error):
                    self.execute(api, route, **params)
                self.assertEqual(self.execute("marks", "get", **self.target).value, 8)
                self.assertEqual(self.total().total_score, 20)

    def test_model_setters_preserve_invariants(self):
        with self.assertRaises(RuleViolationError):
            Score(12, MaxScore(10))
        self.assertEqual(Score(10, MaxScore(10)).value, 10)

        with self.assertRaises(RuleViolationError):
            Mark(**self.target, value=12)

        self.execute("marks", "add", **self.target, value=8)
        with self.database.session() as session:
            repository = SQLAlchemyMarkRepository(session)
            mark = repository.get((self.student.id, self.course.id, self.homework.id))
            criterion = repository.get_criterion(self.homework.id)
            cases = [
                (mark, "value", 12),
                (mark, "score", Score(12, MaxScore(20))),
                (criterion, "max_score", 7),
                (criterion, "maximum", MaxScore(7)),
            ]
            for entity, attribute, value in cases:
                with self.subTest(attribute=attribute):
                    with self.assertRaises(RuleViolationError):
                        setattr(entity, attribute, value)
            self.assertEqual((mark.value, criterion.max_score), (8, 10))
            self.assertEqual(mark.score, Score(8, MaxScore(10)))
            mark.score = Score(9, MaxScore(10))
            mark.value = 10
            repository.save(mark)

        self.assertEqual(self.execute("marks", "get", **self.target).value, 10)
        self.assertEqual(self.total().total_score, 25)
        self.execute("criteria", "edit", criterion_id=self.homework.id, max_score=12)
        criterion = self.execute(
            "criteria", "edit", criterion_id=self.homework.id, max_score=10
        )
        self.assertEqual(criterion.max_score, 10)


class RepositoryInjectionTests(unittest.TestCase):
    def test_api_accepts_repository_substitute(self):
        repository = create_autospec(StudentRepository, instance=True)
        repository.get.return_value = Student(id=42, name="Иван")

        result = StudentAPI(repository).execute("get", request={"student_id": 42})

        self.assertEqual(result.model_dump(), {"id": 42, "name": "Иван"})
        repository.get.assert_called_once_with(42)
