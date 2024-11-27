from pathlib import Path
from typing import Iterable, Sequence, Type

from claspin.database import Database
from claspin.model.common import BaseModel, Plugin
from claspin.model.datasource import DatasourcePlugin
from claspin.model.query import TimeSeriesQueryPlugin
from claspin.model.variable import ListVariablePlugin
from claspin.plugins import BUILTIN_PLUGINS

STAR_SUFFIX = ".star"
ABSOLUTE_PREFIX = "//"


class File(BaseModel):
    label: str
    path: Path

    def __str__(self) -> str:
        return self.label


class Workspace:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.db = Database()
        self._plugins: list[Type[Plugin]] = []

    def add_plugin(self, plugin: Type[Plugin]) -> None:
        self._plugins.append(plugin)

    @property
    def datasource_plugins(self) -> Sequence[Type[DatasourcePlugin]]:
        return tuple(v for v in self._plugins if issubclass(v, DatasourcePlugin))

    @property
    def time_series_query_plugins(self) -> Sequence[Type[TimeSeriesQueryPlugin]]:
        return tuple(v for v in self._plugins if issubclass(v, TimeSeriesQueryPlugin))

    @property
    def list_variable_plugins(self) -> Sequence[Type[ListVariablePlugin]]:
        return tuple(v for v in self._plugins if issubclass(v, ListVariablePlugin))

    def resolve_file(self, s: str, base: File) -> File:
        if s.startswith(ABSOLUTE_PREFIX):
            path = self.root_dir.joinpath(s[len(ABSOLUTE_PREFIX) :])
            if path.suffix == STAR_SUFFIX and path.is_file():
                return self._make_file(path)
        else:
            path = base.path.parent.joinpath(s)
            if path.suffix == STAR_SUFFIX and path.is_file():
                return self._make_file(path)
        raise ValueError(f"Cannot resolve file: '{s}'")

    def iter_files(self) -> Iterable[File]:
        for path in self.root_dir.iterdir():
            if path.is_file() and path.suffix == STAR_SUFFIX:
                yield self._make_file(path)

    def _make_file(self, path: Path):
        return File(label=f"//{path.relative_to(self.root_dir).with_suffix('')}", path=path)


def create_workspace(root_dir: Path) -> Workspace:
    workspace = Workspace(root_dir)
    for plugin in BUILTIN_PLUGINS:
        workspace.add_plugin(plugin)
    return workspace
