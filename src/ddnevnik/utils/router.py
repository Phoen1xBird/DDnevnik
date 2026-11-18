from collections.abc import Callable
from functools import partial, wraps
from typing import Any

from pydantic import ValidationError, validate_call

from ddnevnik.errors import (
    InvalidParametersError,
    UnknownRouteError,
)


class Router:
    def __init__(self) -> None:
        self._routes: dict[str, Callable[..., Any]] = {}

    def register(
        self,
        name: str,
        handler: Callable[..., Any],
    ) -> None:
        @wraps(handler)
        def prepare_handler(*args: Any, **kwargs: Any) -> Any:
            return partial(handler, *args, **kwargs)

        parse_arguments = validate_call(prepare_handler)

        @wraps(handler)
        def validated_handler(**kwargs: Any) -> Any:
            try:
                invocation = parse_arguments(**kwargs)
            except ValidationError as error:
                details = [
                    dict(item)
                    for item in error.errors(include_url=False, include_input=False)
                ]
                raise InvalidParametersError(name, details) from None

            return invocation()

        self._routes[name] = validated_handler

    def get(self, name: str) -> Callable[..., Any]:
        try:
            return self._routes[name]
        except KeyError:
            raise UnknownRouteError(f"Неизвестный маршрут: {name!r}") from None
