from functools import partial
from pathlib import Path
from typing import Iterable, Type

import starlark as sl

from claspin.database import Database
from claspin.model.common import BaseModel, Metadata, Plugin
from claspin.model.datasource import (
    Datasource,
    DatasourcePlugin,
    DatasourcePluginDefinition,
    DatasourceSpec,
)
from claspin.model.query import (
    Query,
    TimeSeriesQuery,
    TimeSeriesQueryPlugin,
    TimeSeriesQueryPluginDefinition,
    TimeSeriesQuerySpec,
)
from claspin.model.variable import (
    ListVariable,
    ListVariablePlugin,
    ListVariablePluginDefinition,
    ListVariableSpec,
    Variable,
)
from claspin.plugins import BUILTIN_PLUGINS


class Workspace:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.db = Database()
        self._plugins: list[Type[Plugin]] = []
        self._globals = sl.Globals.standard()
        self._file_loader = sl.FileLoader(self._load_file)

    def add_plugin(self, plugin: Type[Plugin]) -> None:
        self._plugins.append(plugin)

    def load(self):
        for target in self._collect_targets():
            self._load_file(target)

    def lint(self) -> list[sl.Lint]:
        result: list[sl.Lint] = []
        for target in self._collect_targets():
            ast = self._parse_file(target)
            result.extend(ast.lint())
        return result

    def _parse_file(self, name: str) -> sl.AstModule:
        if name.startswith("//"):
            filepath = self.root_dir.joinpath(name[2:])
            if not filepath.is_file():
                raise FileNotFoundError(name)
            return sl.parse(name, filepath.read_text())
        else:
            raise ValueError(f"Invalid label: '{name}'")

    def _load_file(self, name: str) -> sl.FrozenModule:
        ast = self._parse_file(name)
        module = self._create_module()
        sl.eval(module, ast, self._globals, self._file_loader)
        return module.freeze()

    def _create_module(self) -> sl.Module:
        module = sl.Module()

        def datasource_factory(plugin: type[DatasourcePlugin], name: str, props: dict):
            plugin_def = DatasourcePluginDefinition(spec=self._model_validate(plugin, props))
            spec = self._model_validate(DatasourceSpec, props | {"plugin": plugin_def})
            datasource = Datasource(metadata=Metadata(name=name), spec=spec)
            self.db.save(datasource)

        for plugin in self._datasource_plugins:
            module.add_callable(
                plugin.method_name(),
                partial(datasource_factory, plugin),
            )

        def time_series_query_factory(
            plugin: type[TimeSeriesQueryPlugin],
            name: str,
            props: dict,
        ):
            plugin_def = TimeSeriesQueryPluginDefinition(spec=self._model_validate(plugin, props))
            spec = self._model_validate(TimeSeriesQuerySpec, props | {"plugin": plugin_def})
            query = Query(
                metadata=Metadata(name=name),
                spec=TimeSeriesQuery(spec=spec),
            )
            self.db.save(query)

        for plugin in self._time_series_query_plugins:
            module.add_callable(
                plugin.method_name(),
                partial(time_series_query_factory, plugin),
            )

        def list_variable_factory(
            plugin: type[ListVariablePlugin],
            name: str,
            props: dict,
        ):
            plugin_def = ListVariablePluginDefinition(spec=self._model_validate(plugin, props))
            spec = self._model_validate(ListVariableSpec, props | {"plugin": plugin_def})
            variable = Variable(
                metadata=Metadata(name=name),
                spec=ListVariable(spec=spec),
            )
            self.db.save(variable)

        for plugin in self._list_variable_plugins:
            module.add_callable(
                plugin.method_name(),
                partial(list_variable_factory, plugin),
            )

        return module

    def _model_validate[T: BaseModel](self, typ: Type[T], props: dict) -> T:
        obj = {k: v for k, v in props.items() if k in typ.model_fields}
        return typ.model_validate(obj)

    def _collect_targets(self) -> Iterable[str]:
        for filepath in self.root_dir.iterdir():
            if filepath.suffix == ".star":
                yield f"//{filepath.relative_to(self.root_dir)}"

    @property
    def _datasource_plugins(self) -> list[Type[DatasourcePlugin]]:
        return [v for v in self._plugins if issubclass(v, DatasourcePlugin)]

    @property
    def _time_series_query_plugins(self) -> list[Type[TimeSeriesQueryPlugin]]:
        return [v for v in self._plugins if issubclass(v, TimeSeriesQueryPlugin)]

    @property
    def _list_variable_plugins(self) -> list[Type[ListVariablePlugin]]:
        return [v for v in self._plugins if issubclass(v, ListVariablePlugin)]


def create_workspace(root_dir: Path) -> Workspace:
    workspace = Workspace(root_dir)
    for plugin in BUILTIN_PLUGINS:
        workspace.add_plugin(plugin)
    return workspace
