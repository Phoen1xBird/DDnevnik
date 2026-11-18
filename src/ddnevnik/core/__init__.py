from .base import API
from .course import CourseAPI
from .criteria import CriteriaAPI
from .mark import MarkAPI
from .results import ResultsAPI
from ddnevnik.utils.route import route
from ddnevnik.utils.router import Router
from .student import StudentAPI

__all__ = [
    "API",
    "CourseAPI",
    "CriteriaAPI",
    "MarkAPI",
    "ResultsAPI",
    "Router",
    "StudentAPI",
    "route",
]
