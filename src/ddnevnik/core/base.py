from inspect import getmembers, isfunction
from typing import Any, Generic, TypeVar

from ddnevnik.utils.route import ROUTE_ATTRIBUTE
from ddnevnik.utils.router import Router

RepositoryT = TypeVar("RepositoryT")


class API(Generic[RepositoryT]):
    def __init__(self, repository: RepositoryT) -> None:
        self.repository = repository
        self.router = Router()

        for method_name, method in getmembers(type(self), predicate=isfunction):
            route_name = getattr(method, ROUTE_ATTRIBUTE, None)
            if route_name is not None:
                self.router.register(
                    route_name,
                    getattr(self, method_name),
                )

    def execute(self, router_name: str, /, **kwargs: Any) -> Any:
        handler = self.router.get(router_name)
        return handler(**kwargs)
