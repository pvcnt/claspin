from copy import deepcopy
from functools import partial

import starlark as sl

from claspin.config.graph import Graph, Node, NodeKey
from claspin.database import Database
from claspin.model import Resource
from claspin.model.common import DEFAULT_PROJECT, Display, Metadata
from claspin.model.dashboard import Dashboard
from claspin.model.datasource import Datasource, DatasourcePluginDefinition, DatasourceSpec
from claspin.model.panel import Panel, PanelPluginDefinition, PanelSpec
from claspin.model.query import Query, TimeSeriesQuery, TimeSeriesQueryPluginDefinition, TimeSeriesQuerySpec
from claspin.model.variable import (
    ListVariable,
    ListVariablePluginDefinition,
    ListVariableSpec,
    TextVariable,
    TextVariableSpec,
    Variable,
)
from claspin.plugins.interface import Plugin
from claspin.workspace import ConfigFile, Workspace


class ConfigParser:
    def __init__(self, workspace: Workspace, db: Database) -> None:
        self._workspace = workspace
        self._db = db
        self._globals = sl.Globals.standard()

    def eval(self) -> None:
        graph = Graph()
        for file in self._workspace.iter_files():
            self._eval_file(file, graph)
        # TODO: topological sort
        for node in graph.nodes:
            self._db.create(self._make_resource(graph, node))

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
        project = DEFAULT_PROJECT

        def package(props: dict):
            global project
            project = props.pop("default_project", DEFAULT_PROJECT)

        module.add_callable("package", package)

        def add_node(plugin: Plugin | None, kind: str, name: str, props: dict):
            key = NodeKey(kind=kind, project=project, path=file.path, name=name)
            graph.add_node(Node(key=key, props=props, plugin=plugin))

        def add_node_with_deps(
            plugin: Plugin | None,
            kind: str,
            dep_kind: str,
            name: str,
            props: dict,
            deps: list[str],
        ):
            key = NodeKey(kind=kind, project=project, path=file.path, name=name)
            graph.add_node(Node(key=key, props=props, plugin=plugin))
            for dep in deps:
                graph.add_edge(key, NodeKey(kind=dep_kind, project=project, path=file.path, name=dep))

        module.add_callable(
            "text_variable",
            partial(add_node, None, Variable.kind()),
        )

        module.add_callable(
            "dashboard",
            partial(add_node, None, Dashboard.kind()),
        )

        for plugin in self._workspace.datasource_plugins:
            module.add_callable(
                plugin.method_name,
                partial(add_node, plugin, Datasource.kind()),
            )

        for plugin in self._workspace.time_series_query_plugins:
            module.add_callable(
                plugin.method_name,
                partial(add_node, plugin, Query.kind()),
            )

        for plugin in self._workspace.list_variable_plugins:
            module.add_callable(
                plugin.method_name,
                partial(add_node, plugin, Variable.kind()),
            )

        for plugin in self._workspace.panel_plugins:
            module.add_callable(
                plugin.method_name,
                partial(add_node_with_deps, plugin, Panel.kind(), Query.kind()),
            )

        return module

    def _make_resource(self, graph: Graph, node: Node) -> Resource:
        if node.key.kind == Datasource.kind():
            return self._make_datasource(node)
        elif node.key.kind == Variable.kind():
            return self._make_variable(node)
        elif node.key.kind == Query.kind():
            return self._make_query(node)
        elif node.key.kind == Panel.kind():
            return self._make_panel(graph, node)
        else:
            raise AssertionError()

    def _make_datasource(self, node: Node) -> Datasource:
        assert node.plugin is not None
        plugin = DatasourcePluginDefinition(kind=node.plugin.kind, spec=node.plugin.eval(node.props))
        spec = DatasourceSpec(plugin=plugin)
        return Datasource(metadata=self._make_metadata(node), spec=spec)

    def _make_variable(self, node: Node) -> Variable:
        props = deepcopy(node.props)
        display = Display(
            name=props.pop("display_name", None),
            description=props.pop("description", None),
            hidden=props.pop("hidden", None),
        )
        if node.plugin is None:
            spec = TextVariable(
                spec=TextVariableSpec(
                    name=node.key.name,
                    display=display,
                    value=props.pop("value", None),
                    constant=props.pop("constant", None),
                ),
            )
        else:
            spec = ListVariable(
                spec=ListVariableSpec(
                    name=node.key.name,
                    display=display,
                    default_value=props.pop("default_value", None),
                    allow_all_value=props.pop("allow_all_value", None),
                    allow_multiple=props.pop("allow_multiple", None),
                    custom_all_value=props.pop("custom_all_value", None),
                    capturing_regexp=props.pop("capturing_regexp", None),
                    plugin=ListVariablePluginDefinition(
                        kind=node.plugin.kind,
                        spec=node.plugin.eval(props),
                    ),
                ),
            )
        return Variable(metadata=self._make_metadata(node), spec=spec)

    def _make_query(self, node: Node) -> Query:
        assert node.plugin is not None
        spec = TimeSeriesQuery(
            spec=TimeSeriesQuerySpec(
                plugin=TimeSeriesQueryPluginDefinition(
                    kind=node.plugin.kind,
                    spec=node.plugin.eval(node.props),
                ),
            ),
        )
        return Query(metadata=self._make_metadata(node), spec=spec)

    def _make_panel(self, graph: Graph, node: Node) -> Panel:
        assert node.plugin is not None
        props = deepcopy(node.props)
        display = Display(
            name=props.pop("display_name", None),
            description=props.pop("description", None),
            hidden=props.pop("hidden", None),
        )
        plugin = PanelPluginDefinition(kind=node.plugin.kind, spec=node.plugin.eval(node.props))
        queries = [self._db.get(Query, node.key.name, node.key.project) for node in graph.successors(node.key)]
        spec = PanelSpec(plugin=plugin, display=display, queries=[q.spec for q in queries if q])
        return Panel(metadata=self._make_metadata(node), spec=spec)

    def _make_metadata(self, node: Node) -> Metadata:
        # TODO: include package "somewhere"
        return Metadata(name=node.key.name)

    def _remove_none(self, props: dict) -> dict:
        return {k: self._remove_none(v) if isinstance(v, dict) else v for k, v in props.items() if v is not None}
