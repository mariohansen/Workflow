from __future__ import annotations

from uuid import uuid4

from app.domain.graph import Edge, Graph, Node, Position, validate_graph


def make_node(node_type: str = "text_input") -> Node:
    return Node(id=uuid4(), type=node_type, position=Position(0, 0), config={})


def test_empty_graph_is_valid() -> None:
    assert validate_graph(Graph(nodes=[], edges=[])) == []


def test_acyclic_graph_is_valid() -> None:
    a, b, c = make_node(), make_node(), make_node()
    edges = [
        Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=b.id, to_port="in"),
        Edge(id=uuid4(), from_node=b.id, from_port="out", to_node=c.id, to_port="in"),
    ]

    assert validate_graph(Graph(nodes=[a, b, c], edges=edges)) == []


def test_cycle_is_rejected() -> None:
    a, b = make_node(), make_node()
    edges = [
        Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=b.id, to_port="in"),
        Edge(id=uuid4(), from_node=b.id, from_port="out", to_node=a.id, to_port="in"),
    ]

    violations = validate_graph(Graph(nodes=[a, b], edges=edges))

    assert [v.code for v in violations] == ["cycle"]


def test_self_loop_is_rejected_as_cycle() -> None:
    a = make_node()
    edges = [Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=a.id, to_port="in")]

    violations = validate_graph(Graph(nodes=[a], edges=edges))

    assert [v.code for v in violations] == ["cycle"]


def test_edge_to_unknown_node_is_rejected() -> None:
    a = make_node()
    edges = [Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=uuid4(), to_port="in")]

    violations = validate_graph(Graph(nodes=[a], edges=edges))

    assert [v.code for v in violations] == ["unknown_node"]


def test_diamond_graph_is_valid() -> None:
    a, b, c, d = make_node(), make_node(), make_node(), make_node()
    edges = [
        Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=b.id, to_port="in"),
        Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=c.id, to_port="in"),
        Edge(id=uuid4(), from_node=b.id, from_port="out", to_node=d.id, to_port="in"),
        Edge(id=uuid4(), from_node=c.id, from_port="out", to_node=d.id, to_port="in"),
    ]

    assert validate_graph(Graph(nodes=[a, b, c, d], edges=edges)) == []


def test_reports_all_violations_not_just_the_first() -> None:
    a, b = make_node(), make_node()
    edges = [
        Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=uuid4(), to_port="in"),
        Edge(id=uuid4(), from_node=uuid4(), from_port="out", to_node=b.id, to_port="in"),
    ]

    violations = validate_graph(Graph(nodes=[a, b], edges=edges))

    assert len(violations) == 2
