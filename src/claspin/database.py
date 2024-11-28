from collections import defaultdict
from typing import Iterable, Type, cast

from claspin.model.common import DEFAULT_PROJECT, Entity, Metadata
from claspin.model.project import Project


class Database:
    def __init__(self) -> None:
        self._entities: dict[str, dict[str, Entity]] = defaultdict(dict)
        self.create(Project(metadata=Metadata(name=DEFAULT_PROJECT)))

    @property
    def entities(self) -> Iterable[Entity]:
        for res in self._entities.values():
            yield from res.values()

    def create(self, entity: Entity) -> None:
        key = self._make_key(entity)
        self._entities[entity.kind()][key] = entity

    def upsert(self, entity: Entity) -> None:
        key = self._make_key(entity)
        self._entities[entity.kind()][key] = entity

    def query[T: Entity](self, typ: Type[T], project_name: str | None = None) -> Iterable[T]:
        for res in self._entities[typ.kind()].values():
            if project_name is None or res.metadata.project == project_name:
                yield cast(T, res)

    def get[T: Entity](self, typ: Type[T], name: str, project_name: str | None = None) -> T | None:
        key = name if project_name is None else f"{project_name}/{name}"
        resource = self._entities[typ.kind()].get(key)
        return cast(T, resource) if resource is not None else None

    def _make_key(self, resource: Entity) -> str:
        return (
            resource.metadata.name
            if resource.metadata.project is None
            else f"{resource.metadata.project}/{resource.metadata.name}"
        )
