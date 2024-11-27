from collections import defaultdict
from typing import Iterable, Type, cast

from claspin.model import Resource
from claspin.model.common import Kind
from claspin.model.project import DEFAULT_PROJECT


class Database:
    def __init__(self) -> None:
        self._resources: dict[Kind, dict[str, Resource]] = defaultdict(dict)
        self.save(DEFAULT_PROJECT)

    @property
    def resources(self) -> Iterable[Resource]:
        for res in self._resources.values():
            yield from res.values()

    def save(self, resource: Resource) -> None:
        key = (
            resource.metadata.name
            if resource.metadata.project is None
            else f"{resource.metadata.project}/{resource.metadata.name}"
        )
        self._resources[resource.kind][key] = resource

    def query[T: Resource](self, typ: Type[T], project_name: str | None = None) -> Iterable[T]:
        kind = cast(Kind, typ.model_fields["kind"].default)
        for res in self._resources[kind].values():
            if project_name is None or res.metadata.project == project_name:
                yield cast(T, res)

    def get[T: Resource](self, typ: Type[T], name: str, project_name: str | None = None) -> T | None:
        kind = cast(Kind, typ.model_fields["kind"].default)
        key = name if project_name is None else f"{project_name}/{name}"
        resource = self._resources[kind].get(key)
        return cast(T, resource) if resource is not None else None
