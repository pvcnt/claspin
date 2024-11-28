from dataclasses import dataclass
from typing import Iterable

from claspin.plugins.interface import Plugin


@dataclass(frozen=True)
class NodeKey:
    kind: str
    project: str
    path: str
    name: str

    @property
    def label(self) -> str:
        return f"//{self.path}:{self.name}"


@dataclass(frozen=True)
class Node:
    key: NodeKey
    props: dict
    # TODO: store reference to plugin, not plugin itself
    plugin: Plugin | None = None


@dataclass(frozen=True)
class Edge:
    parent: NodeKey
    child: NodeKey


class Graph:
    def __init__(self) -> None:
        self._nodes: dict[NodeKey, Node] = {}
        self._edges: set[Edge] = set()

    @property
    def nodes(self) -> Iterable[Node]:
        return self._nodes.values()

    def successors(self, parent: NodeKey) -> Iterable[Node]:
        return tuple(self._nodes[edge.child] for edge in self._edges if edge.parent == parent)

    def add_node(self, node: Node) -> None:
        self._nodes[node.key] = node

    def add_edge(self, parent: NodeKey, child: NodeKey) -> None:
        self._edges.add(Edge(parent=parent, child=child))
