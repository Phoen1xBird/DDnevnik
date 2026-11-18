from collections.abc import Callable
from typing import ParamSpec, TypeVar

from ddnevnik.errors import RouteRegistrationError

P = ParamSpec("P")
R = TypeVar("R")
ROUTE_ATTRIBUTE = "__ddnevnik_route__"


def route(name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    if not isinstance(name, str) or not name.strip():
        raise RouteRegistrationError("Имя маршрута должно быть непустой строкой")

    def decorate(method: Callable[P, R]) -> Callable[P, R]:
        if hasattr(method, ROUTE_ATTRIBUTE):
            raise RouteRegistrationError("У метода уже зарегистрирован маршрут")
        setattr(method, ROUTE_ATTRIBUTE, name)
        return method

    return decorate
