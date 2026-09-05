from __future__ import annotations

from uuid import UUID

from app.domain.graph import Graph


def ready_nodes(graph: Graph, completed: frozenset[UUID]) -> list[UUID]:
    """Nodes whose predecessors are all completed and that aren't completed
    themselves. Recomputed after every step - levels are planning, not a
    barrier, so independent branches never wait on each other."""
    predecessors: dict[UUID, set[UUID]] = {node.id: set() for node in graph.nodes}
    for edge in graph.edges:
        if edge.to_node in predecessors:
            predecessors[edge.to_node].add(edge.from_node)

    return [
        node_id
        for node_id, preds in predecessors.items()
        if node_id not in completed and preds <= completed
    ]


def downstream_nodes(graph: Graph, node_id: UUID) -> set[UUID]:
    """Every node reachable from `node_id` via forward edges - used to mark
    dependents SKIPPED when a step fails, without touching independent branches."""
    adjacency: dict[UUID, list[UUID]] = {node.id: [] for node in graph.nodes}
    for edge in graph.edges:
        if edge.from_node in adjacency:
            adjacency[edge.from_node].append(edge.to_node)

    seen: set[UUID] = set()
    stack = list(adjacency.get(node_id, []))
    while stack:
        current = stack.pop()
        if current not in seen:
            seen.add(current)
            stack.extend(adjacency.get(current, []))

    return seen
