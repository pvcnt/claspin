from functools import partial
from typing import Type

import starlark as sl

from claspin.config.graph import Graph, Node, NodeKey
from claspin.model.common import Plugin
from claspin.model.datasource import Datasource
from claspin.model.query import Query
from claspin.model.variable import Variable
from claspin.workspace import ConfigFile, Workspace


class ConfigParser:
    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace
        self._globals = sl.Globals.standard()

    def eval(self) -> Graph:
        graph = Graph()
        for file in self._workspace.iter_files():
            self._eval_file(file, graph)
        return graph

    def lint(self) -> list[sl.Lint]:
        result: list[sl.Lint] = []
        for file in self._workspace.iter_files():
            ast = self._parse_file(file)
            result.extend(ast.lint())
        return result

    def _parse_file(self, file: ConfigFile) -> sl.AstModule:
        return sl.parse(file.label, file.content)

    def _eval_file(self, file: ConfigFile, graph: Graph) -> sl.FrozenModule:
        ast = self._parse_file(file)
        module = self._make_module(file, graph)
        file_loader = sl.FileLoader(lambda s: self._eval_file(self._workspace.resolve_file(s, file), graph))
        sl.eval(module, ast, self._globals, file_loader)
        return module.freeze()

    def _make_module(self, file: ConfigFile, graph: Graph) -> sl.Module:
        module = sl.Module()

        def add_node(plugin: Type[Plugin] | None, kind: str, name: str, props: dict) -> None:
            key = NodeKey(kind=kind, path=file.path, name=name)
            graph.add_node(Node(key=key, props=props, plugin=plugin))

        module.add_callable(
            "text_variable",
            partial(add_node, None, Variable.kind()),
        )

        for plugin in self._workspace.datasource_plugins:
            module.add_callable(
                plugin.method_name(),
                partial(add_node, plugin, Datasource.kind()),
            )

        for plugin in self._workspace.time_series_query_plugins:
            module.add_callable(
                plugin.method_name(),
                partial(add_node, plugin, Query.kind()),
            )

        for plugin in self._workspace.list_variable_plugins:
            module.add_callable(
                plugin.method_name(),
                partial(add_node, plugin, Variable.kind()),
            )

        return module

    def _remove_none(self, props: dict) -> dict:
        return {k: self._remove_none(v) if isinstance(v, dict) else v for k, v in props.items() if v is not None}
