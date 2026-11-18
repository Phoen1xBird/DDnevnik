from enum import Enum

from pydantic import BaseModel, ConfigDict

from .base import EntityId, InputSchema


class TotalMethod(str, Enum):
    WEIGHTED = "weighted"
    POINTS = "points"


class GetCourseResults(InputSchema):
    course_id: EntityId
    strategy: TotalMethod = TotalMethod.WEIGHTED


class GetStudentResults(InputSchema):
    student_id: EntityId
    strategy: TotalMethod = TotalMethod.WEIGHTED


class GetStudentCourseResults(InputSchema):
    student_id: EntityId
    course_id: EntityId
    strategy: TotalMethod = TotalMethod.WEIGHTED


class ResultSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class StudentResult(ResultSchema):
    id: int
    name: str


class CourseResult(ResultSchema):
    id: int
    name: str


class CriterionResult(ResultSchema):
    id: int
    name: str
    max_score: int


class EnrollmentResult(ResultSchema):
    student_id: int
    course_id: int


class CourseCriterionResult(ResultSchema):
    course_id: int
    criterion_id: int
    name: str
    max_score: int
    weight: float


class MarkResult(ResultSchema):
    student_id: int
    course_id: int
    criterion_id: int
    value: int


class TotalResult(ResultSchema):
    student_id: int
    course_id: int
    total_score: float | None
    completed_criteria: int
    total_criteria: int


class CourseTotalsResult(ResultSchema):
    columns: list[str]
    rows: list[dict[str, int | float | str | None]]
