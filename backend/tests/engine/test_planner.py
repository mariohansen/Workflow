from __future__ import annotations

from uuid import uuid4

from app.domain.graph import Edge, Graph, Node, Position
from app.engine.planner import downstream_nodes, ready_nodes


def make_node() -> Node:
    return Node(id=uuid4(), type="x", position=Position(0, 0), config={})


def test_ready_nodes_with_no_predecessors_are_all_ready() -> None:
    a, b = make_node(), make_node()
    graph = Graph(nodes=[a, b], edges=[])

    assert set(ready_nodes(graph, frozenset())) == {a.id, b.id}


def test_ready_nodes_waits_for_predecessor() -> None:
    a, b = make_node(), make_node()
    edges = [Edge(id=uuid4(), from_node=a.id, from_port="o", to_node=b.id, to_port="i")]
    graph = Graph(nodes=[a, b], edges=edges)

    assert ready_nodes(graph, frozenset()) == [a.id]
    assert ready_nodes(graph, frozenset({a.id})) == [b.id]


def test_ready_nodes_excludes_already_completed() -> None:
    a = make_node()
    graph = Graph(nodes=[a], edges=[])

    assert ready_nodes(graph, frozenset({a.id})) == []


def test_ready_nodes_recomputed_after_partial_completion() -> None:
    a, b, c = make_node(), make_node(), make_node()
    edges = [
        Edge(id=uuid4(), from_node=a.id, from_port="o", to_node=c.id, to_port="i"),
        Edge(id=uuid4(), from_node=b.id, from_port="o", to_node=c.id, to_port="i"),
    ]
    graph = Graph(nodes=[a, b, c], edges=edges)

    assert set(ready_nodes(graph, frozenset())) == {a.id, b.id}
    assert ready_nodes(graph, frozenset({a.id})) == [b.id]
    assert ready_nodes(graph, frozenset({a.id, b.id})) == [c.id]


def test_downstream_nodes_follows_the_chain() -> None:
    a, b, c = make_node(), make_node(), make_node()
    edges = [
        Edge(id=uuid4(), from_node=a.id, from_port="o", to_node=b.id, to_port="i"),
        Edge(id=uuid4(), from_node=b.id, from_port="o", to_node=c.id, to_port="i"),
    ]
    graph = Graph(nodes=[a, b, c], edges=edges)

    assert downstream_nodes(graph, a.id) == {b.id, c.id}


def test_downstream_nodes_excludes_independent_branch() -> None:
    a, b, c = make_node(), make_node(), make_node()
    edges = [Edge(id=uuid4(), from_node=a.id, from_port="o", to_node=b.id, to_port="i")]
    graph = Graph(nodes=[a, b, c], edges=edges)

    assert downstream_nodes(graph, a.id) == {b.id}


def test_downstream_nodes_of_leaf_is_empty() -> None:
    a = make_node()
    graph = Graph(nodes=[a], edges=[])

    assert downstream_nodes(graph, a.id) == set()
