from functools import partial
from typing import Iterable

import starlark as sl

from claspin.model.common import Metadata
from claspin.model.datasource import (
    Datasource,
    DatasourcePlugin,
    DatasourceSpec,
)
from claspin.model.query import (
    Query,
    TimeSeriesQuery,
    TimeSeriesQueryPlugin,
    TimeSeriesQuerySpec,
)
from claspin.model.variable import (
    ListVariable,
    ListVariablePlugin,
    ListVariableSpec,
    TextVariable,
    TextVariableSpec,
    Variable,
)
from claspin.workspace import File, Workspace


class ConfigParser:
    def __init__(self, workspace: Workspace) -> None:
        self.workspace = workspace
        self._globals = sl.Globals.standard()

    def load(self):
        for file in self.workspace.iter_files():
            self._load_file(file)

    def lint(self) -> list[sl.Lint]:
        result: list[sl.Lint] = []
        for file in self.workspace.iter_files():
            ast = self._parse_file(file)
            result.extend(ast.lint())
        return result

    def _parse_file(self, file: File) -> sl.AstModule:
        return sl.parse(file.label, file.path.read_text())

    def _load_file(self, file: File) -> sl.FrozenModule:
        ast = self._parse_file(file)
        module = self._make_module()
        file_loader = sl.FileLoader(lambda s: self._load_file(self.workspace.resolve_file(s, file)))
        sl.eval(module, ast, self._globals, file_loader)
        return module.freeze()

    def _make_module(self) -> sl.Module:
        module = sl.Module()

        def datasource_factory(plugin: type[DatasourcePlugin], name: str, props: dict):
            obj = {
                "plugin": {
                    "spec": plugin.model_validate(props),
                },
            }
            spec = DatasourceSpec.model_validate(self._remove_none(obj))
            datasource = Datasource(metadata=Metadata(name=name), spec=spec)
            self.workspace.db.save(datasource)

        for plugin in self.workspace.datasource_plugins:
            module.add_callable(
                plugin.method_name(),
                partial(datasource_factory, plugin),
            )

        def time_series_query_factory(
            plugin: type[TimeSeriesQueryPlugin],
            name: str,
            props: dict,
        ):
            obj = {
                "plugin": {
                    "spec": plugin.model_validate(props),
                },
            }
            spec = TimeSeriesQuerySpec.model_validate(self._remove_none(obj))
            query = Query(
                metadata=Metadata(name=name),
                spec=TimeSeriesQuery(spec=spec),
            )
            self.workspace.db.save(query)

        for plugin in self.workspace.time_series_query_plugins:
            module.add_callable(
                plugin.method_name(),
                partial(time_series_query_factory, plugin),
            )

        def list_variable_factory(
            plugin: type[ListVariablePlugin],
            name: str,
            props: dict,
        ):
            obj = {
                "name": name,
                "display": {
                    "name": props.pop("display_name", None),
                    "description": props.pop("description", None),
                    "hidden": props.pop("hidden", None),
                },
                "defaultValue": props.pop("default_value", None),
                "allowAllValue": props.pop("allow_all_value", None),
                "allowMultiple": props.pop("allow_multiple", None),
                "customAllValue": props.pop("custom_all_value", None),
                "capturingRegexp": props.pop("capturing_regexp", None),
                "plugin": {"spec": plugin.model_validate(props)},
            }
            spec = ListVariableSpec.model_validate(self._remove_none(obj))
            variable = Variable(
                metadata=Metadata(name=name),
                spec=ListVariable(spec=spec),
            )
            self.workspace.db.save(variable)

        for plugin in self.workspace.list_variable_plugins:
            module.add_callable(
                plugin.method_name(),
                partial(list_variable_factory, plugin),
            )

        def text_variable_factory(name: str, props: dict):
            obj = {
                "name": name,
                "display": {
                    "name": props.pop("display_name", None),
                    "description": props.pop("description", None),
                    "hidden": props.pop("hidden", None),
                },
                "value": props.pop("value", None),
                "constant": props.pop("constant", None),
            }
            spec = TextVariableSpec.model_validate(self._remove_none(obj))
            variable = Variable(metadata=Metadata(name=name), spec=TextVariable(spec=spec))
            self.workspace.db.save(variable)

        module.add_callable("text_variable", text_variable_factory)

        return module

    def _collect_targets(self) -> Iterable[str]:
        for filepath in self.workspace.root_dir.iterdir():
            if filepath.suffix == ".star":
                yield f"//{filepath.relative_to(self.workspace.root_dir)}"

    def _remove_none(self, props: dict) -> dict:
        return {k: self._remove_none(v) if isinstance(v, dict) else v for k, v in props.items() if v is not None}
