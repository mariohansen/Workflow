from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class Position:
    x: float
    y: float


@dataclass(frozen=True)
class Node:
    id: UUID
    type: str
    position: Position
    config: Mapping[str, Any]


@dataclass(frozen=True)
class Edge:
    id: UUID
    from_node: UUID
    from_port: str
    to_node: UUID
    to_port: str


@dataclass(frozen=True)
class Graph:
    nodes: Sequence[Node]
    edges: Sequence[Edge]


@dataclass(frozen=True)
class GraphViolation:
    code: str
    message: str


def validate_graph(graph: Graph) -> list[GraphViolation]:
    node_ids = {node.id for node in graph.nodes}
    violations = list(_unknown_node_violations(graph, node_ids))

    if _has_cycle(graph, node_ids):
        violations.append(GraphViolation("cycle", "workflow graph contains a cycle"))

    return violations


def _unknown_node_violations(graph: Graph, node_ids: set[UUID]) -> list[GraphViolation]:
    violations: list[GraphViolation] = []
    for edge in graph.edges:
        if edge.from_node not in node_ids:
            violations.append(
                GraphViolation(
                    "unknown_node", f"edge {edge.id} references unknown node {edge.from_node}"
                )
            )
        if edge.to_node not in node_ids:
            violations.append(
                GraphViolation(
                    "unknown_node", f"edge {edge.id} references unknown node {edge.to_node}"
                )
            )
    return violations


def _has_cycle(graph: Graph, node_ids: set[UUID]) -> bool:
    adjacency: dict[UUID, list[UUID]] = {node_id: [] for node_id in node_ids}
    for edge in graph.edges:
        if edge.from_node in adjacency and edge.to_node in adjacency:
            adjacency[edge.from_node].append(edge.to_node)

    unvisited, in_progress, done = 0, 1, 2
    state: dict[UUID, int] = dict.fromkeys(adjacency, unvisited)

    def visit(node_id: UUID) -> bool:
        state[node_id] = in_progress
        for neighbor in adjacency[node_id]:
            if state[neighbor] == in_progress:
                return True
            if state[neighbor] == unvisited and visit(neighbor):
                return True
        state[node_id] = done
        return False

    return any(state[node_id] == unvisited and visit(node_id) for node_id in adjacency)
