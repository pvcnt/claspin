from dataclasses import dataclass
from typing import Iterable, Type

from claspin.model.common import Plugin


@dataclass(frozen=True)
class NodeKey:
    kind: str
    path: str
    name: str

    @property
    def label(self) -> str:
        return f"//{self.path}:{self.name}"


@dataclass(frozen=True)
class Node:
    key: NodeKey
    props: dict
    plugin: Type[Plugin] | None = None


@dataclass(frozen=True)
class Edge:
    parent: NodeKey
    child: NodeKey
    title: str | None = None


class Graph:
    def __init__(self) -> None:
        self._nodes: dict[NodeKey, Node] = {}
        self._edges: set[Edge] = set()

    @property
    def nodes(self) -> Iterable[Node]:
        return self._nodes.values()

    def add_node(self, node: Node) -> None:
        self._nodes[node.key] = node
