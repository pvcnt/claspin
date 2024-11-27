from typing import Iterable

from claspin.model import Resource
from claspin.model.datasource import Datasource
from claspin.model.query import Query
from claspin.model.variable import Variable


class Database:
    def __init__(self) -> None:
        self._datasources: dict[str, Datasource] = {}
        self._queries: dict[str, Query] = {}
        self._variables: dict[str, Variable] = {}

    def save(self, resource: Resource) -> None:
        if resource.kind == "Datasource":
            self._datasources[resource.metadata.name] = resource
        elif resource.kind == "Query":
            self._queries[resource.metadata.name] = resource
        elif resource.kind == "Variable":
            self._variables[resource.metadata.name] = resource
        else:
            raise AssertionError()

    @property
    def datasources(self) -> Iterable[Datasource]:
        return self._datasources.values()

    def get_datasource(self, name: str) -> Datasource | None:
        return self._datasources.get(name)

    @property
    def queries(self) -> Iterable[Query]:
        return self._queries.values()

    def get_query(self, name: str) -> Query | None:
        return self._queries.get(name)

    @property
    def variables(self) -> Iterable[Variable]:
        return self._variables.values()

    def get_variable(self, name: str) -> Variable | None:
        return self._variables.get(name)

    @property
    def resources(self) -> Iterable[Resource]:
        for seq in (self.datasources, self.queries, self.variables):
            yield from seq
