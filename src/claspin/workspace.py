from functools import partial
from pathlib import Path
from typing import Iterable, Type

import starlark as sl

from claspin.database import Database
from claspin.model.common import BaseModel, Metadata
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
from claspin.plugins import BUILTIN_EXTENSIONS
from claspin.plugins.interface import Extension


class Workspace:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.db = Database()
        self._extensions: dict[str, Extension] = {}
        self._globals = sl.Globals.standard()
        self._file_loader = sl.FileLoader(self._load_file)

    def add_extension(self, extension: Extension) -> None:
        self._extensions[extension.name] = extension

    def parse(self):
        for filepath in self._collect_files():
            self._load_file(f"//{filepath}")

    def lint(self) -> list[sl.Lint]:
        result: list[sl.Lint] = []
        for filepath in self._collect_files():
            ast = sl.parse(str(filepath), filepath.read_text())
            result.extend(ast.lint())
        return result

    def _load_file(self, name: str) -> sl.FrozenModule:
        if name.startswith("//"):
            filepath = self.root_dir.joinpath(name[2:])
            if not filepath.is_file():
                raise FileNotFoundError(name)
            ast = sl.parse(name, filepath.read_text())
            module = self._create_module()
            sl.eval(module, ast, self._globals, self._file_loader)
            return module.freeze()
        else:
            raise ValueError(f"Invalid label: '{name}'")

    def _create_module(self) -> sl.Module:
        module = sl.Module()

        def datasource_factory(plugin: type[DatasourcePlugin], name: str, props: dict):
            plugin_def = DatasourcePluginDefinition(spec=self._model_validate(plugin, props))
            spec = self._model_validate(DatasourceSpec, props | {"plugin": plugin_def})
            datasource = Datasource(metadata=Metadata(name=name), spec=spec)
            self.db.save(datasource)

        for extension in self._extensions.values():
            for plugin in extension.datasource_plugins:
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

        for extension in self._extensions.values():
            for plugin in extension.time_series_query_plugins:
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

        for extension in self._extensions.values():
            for plugin in extension.list_variable_plugins:
                module.add_callable(
                    plugin.method_name(),
                    partial(list_variable_factory, plugin),
                )

        return module

    def _model_validate[T: BaseModel](self, typ: Type[T], props: dict) -> T:
        obj = {k: v for k, v in props.items() if k in typ.model_fields}
        return typ.model_validate(obj)

    def _collect_files(self) -> Iterable[Path]:
        for filepath in self.root_dir.iterdir():
            if filepath.suffix == ".star":
                yield filepath.relative_to(self.root_dir)


def create_workspace(root_dir: Path) -> Workspace:
    workspace = Workspace(root_dir)
    for extension in BUILTIN_EXTENSIONS:
        workspace.add_extension(extension)
    return workspace
