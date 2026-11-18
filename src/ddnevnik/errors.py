from typing import Any


class UnknownAPIError(LookupError):
    pass


class UnknownRouteError(LookupError):
    pass


class RouteRegistrationError(ValueError):
    pass


class IncompleteCommandError(ValueError):
    pass


class NotFoundError(LookupError):
    pass


class AlreadyExistsError(ValueError):
    pass


class RuleViolationError(ValueError):
    pass


class StorageError(RuntimeError):
    pass


class InvalidParametersError(ValueError):

    def __init__(self, route_name: str, details: list[dict[str, Any]]) -> None:
        self.route_name = route_name
        self.details = details

        messages = {
            "missing": "обязательный параметр отсутствует",
            "missing_argument": "обязательный параметр отсутствует",
            "missing_keyword_only_argument": "обязательный параметр отсутствует",
            "missing_positional_only_argument": "обязательный параметр отсутствует",
            "extra_forbidden": "неизвестный параметр",
            "unexpected_keyword_argument": "неизвестный параметр",
            "model_type": "ожидается объект схемы или словарь",
            "int_type": "ожидается целое число",
            "int_parsing": "ожидается целое число",
            "int_from_float": "ожидается целое число",
            "string_type": "ожидается строка",
            "string_too_short": "строка слишком короткая",
            "float_type": "ожидается число",
            "float_parsing": "ожидается число",
            "finite_number": "ожидается конечное число",
        }
        descriptions = []
        for item in details:
            field = ".".join(str(part) for part in item["loc"]) or "параметры"
            message = messages.get(item["type"], item["msg"])
            if item["type"] == "greater_than":
                message = f"значение должно быть больше {item['ctx']['gt']}"
            elif item["type"] == "greater_than_equal":
                message = f"значение должно быть не меньше {item['ctx']['ge']}"
            descriptions.append(f"{field}: {message}")

        super().__init__(
            f"Неверные параметры маршрута {route_name!r}: " + "; ".join(descriptions)
        )
