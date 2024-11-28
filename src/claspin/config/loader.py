from copy import deepcopy

from claspin.config.graph import Graph, Node
from claspin.database import Database
from claspin.model import Resource
from claspin.model.common import Metadata
from claspin.model.datasource import Datasource, DatasourceSpec
from claspin.model.query import Query, TimeSeriesQuery
from claspin.model.variable import ListVariable, TextVariable, Variable


class ConfigLoader:
    def __init__(self, db: Database) -> None:
        self._db = db

    def load(self, graph: Graph) -> None:
        for node in graph.nodes:
            self._db.create(self._make_resource(node))

    def _make_resource(self, node: Node) -> Resource:
        if node.key.kind == Datasource.kind():
            return self._make_datasource(node)
        elif node.key.kind == Variable.kind():
            return self._make_variable(node)
        elif node.key.kind == Query.kind():
            return self._make_query(node)
        else:
            raise AssertionError()

    def _make_datasource(self, node: Node) -> Datasource:
        assert node.plugin is not None
        props = deepcopy(node.props)
        obj = {
            "plugin": {
                "spec": node.plugin.model_validate(props),
            },
        }
        spec = DatasourceSpec.model_validate(self._remove_none(obj))
        return Datasource(metadata=self._make_metadata(node), spec=spec)

    def _make_variable(self, node: Node) -> Variable:
        props = deepcopy(node.props)
        display = {
            "name": props.pop("display_name", None),
            "description": props.pop("description", None),
            "hidden": props.pop("hidden", None),
        }
        if node.plugin is None:
            obj = {
                "spec": {
                    "name": node.key.name,
                    "display": display,
                    "value": props.pop("value", None),
                    "constant": props.pop("constant", None),
                },
            }
            spec = TextVariable.model_validate(self._remove_none(obj))
        else:
            obj = {
                "spec": {
                    "name": node.key.name,
                    "display": display,
                    "defaultValue": props.pop("default_value", None),
                    "allowAllValue": props.pop("allow_all_value", None),
                    "allowMultiple": props.pop("allow_multiple", None),
                    "customAllValue": props.pop("custom_all_value", None),
                    "capturingRegexp": props.pop("capturing_regexp", None),
                    "plugin": {
                        "spec": node.plugin.model_validate(props),
                    },
                },
            }
            spec = ListVariable.model_validate(self._remove_none(obj))
        return Variable(metadata=self._make_metadata(node), spec=spec)

    def _make_query(self, node: Node) -> Query:
        assert node.plugin is not None
        props = deepcopy(node.props)
        obj = {
            "spec": {
                "plugin": {
                    "spec": node.plugin.model_validate(props),
                },
            },
        }
        spec = TimeSeriesQuery.model_validate(self._remove_none(obj))
        return Query(metadata=self._make_metadata(node), spec=spec)

    def _make_metadata(self, node: Node) -> Metadata:
        # TODO: include package "somewhere"
        return Metadata(name=node.key.name)

    def _remove_none(self, props: dict) -> dict:
        return {k: self._remove_none(v) if isinstance(v, dict) else v for k, v in props.items() if v is not None}
