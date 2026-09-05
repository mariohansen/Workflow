from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.domain.ports import NodeType


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


def validate_graph(graph: Graph, node_types: Mapping[str, NodeType]) -> list[GraphViolation]:
    node_ids = {node.id for node in graph.nodes}
    violations = list(_unknown_node_violations(graph, node_ids))
    violations.extend(_unknown_type_violations(graph, node_types))

    if _has_cycle(graph, node_ids):
        violations.append(GraphViolation("cycle", "workflow graph contains a cycle"))

    # port-level rules need every node reference and type to be valid first,
    # otherwise the lookups below would be meaningless
    if not violations:
        violations.extend(_port_violations(graph, node_types))
        violations.extend(_missing_required_input_violations(graph, node_types))
        violations.extend(_missing_output_node_violation(graph, node_types))

    return violations


def _unknown_type_violations(
    graph: Graph, node_types: Mapping[str, NodeType]
) -> list[GraphViolation]:
    return [
        GraphViolation("unknown_node_type", f"node {node.id} has unknown type {node.type!r}")
        for node in graph.nodes
        if node.type not in node_types
    ]


def _port_violations(graph: Graph, node_types: Mapping[str, NodeType]) -> list[GraphViolation]:
    nodes_by_id = {node.id: node for node in graph.nodes}
    violations: list[GraphViolation] = []
    input_connection_counts: Counter[tuple[UUID, str]] = Counter()

    for edge in graph.edges:
        source_type = node_types[nodes_by_id[edge.from_node].type]
        target_type = node_types[nodes_by_id[edge.to_node].type]
        output_port = next((p for p in source_type.outputs if p.name == edge.from_port), None)
        input_port = next((p for p in target_type.inputs if p.name == edge.to_port), None)

        if output_port is None:
            violations.append(
                GraphViolation(
                    "unknown_port",
                    f"edge {edge.id}: {source_type.type} has no output {edge.from_port!r}",
                )
            )
        if input_port is None:
            violations.append(
                GraphViolation(
                    "unknown_port",
                    f"edge {edge.id}: {target_type.type} has no input {edge.to_port!r}",
                )
            )
        if output_port is not None and input_port is not None:
            if output_port.produces not in input_port.accepts:
                violations.append(
                    GraphViolation(
                        "incompatible_port",
                        f"edge {edge.id}: {output_port.produces} is not accepted by "
                        f"{target_type.type}.{input_port.name}",
                    )
                )
            input_connection_counts[(edge.to_node, edge.to_port)] += 1

    for (node_id, port_name), count in input_connection_counts.items():
        target_type = node_types[nodes_by_id[node_id].type]
        input_port = next((p for p in target_type.inputs if p.name == port_name), None)
        if input_port is not None and not input_port.multiple and count > 1:
            violations.append(
                GraphViolation(
                    "port_not_multiple",
                    f"node {node_id}.{port_name} accepts only one connection, got {count}",
                )
            )

    return violations


def _missing_required_input_violations(
    graph: Graph, node_types: Mapping[str, NodeType]
) -> list[GraphViolation]:
    connected_inputs = {(edge.to_node, edge.to_port) for edge in graph.edges}
    violations: list[GraphViolation] = []

    for node in graph.nodes:
        for port in node_types[node.type].inputs:
            if port.required and (node.id, port.name) not in connected_inputs:
                violations.append(
                    GraphViolation(
                        "missing_required_input",
                        f"node {node.id}.{port.name} is required but unconnected",
                    )
                )

    return violations


def _missing_output_node_violation(
    graph: Graph, node_types: Mapping[str, NodeType]
) -> list[GraphViolation]:
    if not graph.nodes:
        return []

    has_output_node = any(len(node_types[node.type].outputs) == 0 for node in graph.nodes)
    if has_output_node:
        return []

    return [GraphViolation("missing_output_node", "workflow graph has no terminal output node")]


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
