from functools import partial
from pathlib import Path
from typing import Iterable

import starlark as sl

from claspin.model import Resource
from claspin.model.common import Metadata
from claspin.model.datasource import (
    Datasource,
    DatasourcePlugin,
    DatasourcePluginModel,
    DatasourceSpec,
)
from claspin.model.query import Query, QueryPlugin, QueryPluginModel, QuerySpec
from claspin.plugins import DATASOURCE_PLUGINS, QUERY_PLUGINS


class Workspace:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self._datasources: dict[str, Datasource] = {}
        self._datasource_plugins: list[type[DatasourcePlugin]] = []
        self._queries: dict[str, Query] = {}
        self._query_plugins: list[type[QueryPlugin]] = []
        self._globals = sl.Globals.standard()

    def add_datasource_plugin(self, plugin: type[DatasourcePlugin]) -> None:
        self._datasource_plugins.append(plugin)

    def add_query_plugin(self, plugin: type[QueryPlugin]) -> None:
        self._query_plugins.append(plugin)

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
    def resources(self) -> Iterable[Resource]:
        for seq in (self.datasources, self.queries):
            yield from seq

    def parse(self):
        file_loader = sl.FileLoader(self._load)
        for filepath in self._collect_files():
            module = self._create_module()
            ast = sl.parse(str(filepath), filepath.read_text())
            sl.eval(module, ast, self._globals, file_loader)

    def lint(self) -> list[sl.Lint]:
        result: list[sl.Lint] = []
        for filepath in self._collect_files():
            ast = sl.parse(str(filepath), filepath.read_text())
            result.extend(ast.lint())
        return result

    def _load(self, name: str) -> sl.FrozenModule:
        filepath = self.root_dir.joinpath(name)
        if filepath.is_file():
            ast = sl.parse(name, filepath.read_text())
            module = self._create_module()
            sl.eval(module, ast, self._globals)
            return module.freeze()
        else:
            raise FileNotFoundError(name)

    def _create_module(self) -> sl.Module:
        module = sl.Module()

        def datasource_factory(plugin: type[DatasourcePlugin], name: str, attrs: dict):
            datasource = Datasource(
                metadata=Metadata(name=name),
                spec=DatasourceSpec(
                    plugin=DatasourcePluginModel(
                        kind=plugin.kind(), spec=plugin.model_validate(attrs)
                    )
                ),
            )
            self._datasources[name] = datasource

        for plugin in self._datasource_plugins:
            module.add_callable(
                plugin.method_name(), partial(datasource_factory, plugin)
            )

        def query_factory(plugin: type[QueryPlugin], name: str, attrs: dict):
            query = Query(
                metadata=Metadata(name=name),
                spec=QuerySpec(
                    plugin=QueryPluginModel(
                        kind=plugin.kind(), spec=plugin.model_validate(attrs)
                    )
                ),
            )
            self._queries[name] = query

        for plugin in self._query_plugins:
            module.add_callable(plugin.method_name(), partial(query_factory, plugin))

        return module

    def _collect_files(self) -> Iterable[Path]:
        for filepath in self.root_dir.iterdir():
            if filepath.suffix == ".star":
                yield filepath


def create_workspace(root_dir: Path) -> Workspace:
    workspace = Workspace(root_dir)
    for plugin in DATASOURCE_PLUGINS:
        workspace.add_datasource_plugin(plugin)
    for plugin in QUERY_PLUGINS:
        workspace.add_query_plugin(plugin)
    return workspace
