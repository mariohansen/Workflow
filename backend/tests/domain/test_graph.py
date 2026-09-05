from __future__ import annotations

from uuid import uuid4

from app.domain.artifacts import ArtifactKind
from app.domain.graph import Edge, Graph, Node, Position, validate_graph
from app.domain.ports import InputPort, NodeType, OutputPort

SOURCE = NodeType(
    type="source",
    label="Source",
    category="test",
    outputs=(OutputPort("out", "Out", ArtifactKind.TEXT),),
)
SINK = NodeType(
    type="sink",
    label="Sink",
    category="test",
    inputs=(InputPort("in", "In", frozenset({ArtifactKind.TEXT})),),
)
RELAY = NodeType(
    type="relay",
    label="Relay",
    category="test",
    inputs=(InputPort("in", "In", frozenset({ArtifactKind.TEXT})),),
    outputs=(OutputPort("out", "Out", ArtifactKind.TEXT),),
)
RELAY_MULTI = NodeType(
    type="relay_multi",
    label="Relay (multiple)",
    category="test",
    inputs=(InputPort("in", "In", frozenset({ArtifactKind.TEXT}), multiple=True),),
    outputs=(OutputPort("out", "Out", ArtifactKind.TEXT),),
)
SINK_JSON_ONLY = NodeType(
    type="sink_json",
    label="Sink (json only)",
    category="test",
    inputs=(InputPort("in", "In", frozenset({ArtifactKind.JSON})),),
)
SINK_MULTI = NodeType(
    type="sink_multi",
    label="Sink (multiple)",
    category="test",
    inputs=(InputPort("in", "In", frozenset({ArtifactKind.TEXT}), multiple=True),),
)
NODE_TYPES = {
    nt.type: nt for nt in (SOURCE, SINK, RELAY, RELAY_MULTI, SINK_JSON_ONLY, SINK_MULTI)
}


def make_node(node_type: str) -> Node:
    return Node(id=uuid4(), type=node_type, position=Position(0, 0), config={})


def test_empty_graph_is_valid() -> None:
    assert validate_graph(Graph(nodes=[], edges=[]), NODE_TYPES) == []


def test_acyclic_graph_is_valid() -> None:
    a, b, c = make_node("source"), make_node("relay"), make_node("sink")
    edges = [
        Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=b.id, to_port="in"),
        Edge(id=uuid4(), from_node=b.id, from_port="out", to_node=c.id, to_port="in"),
    ]

    assert validate_graph(Graph(nodes=[a, b, c], edges=edges), NODE_TYPES) == []


def test_cycle_is_rejected() -> None:
    a, b = make_node("relay"), make_node("relay")
    edges = [
        Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=b.id, to_port="in"),
        Edge(id=uuid4(), from_node=b.id, from_port="out", to_node=a.id, to_port="in"),
    ]

    violations = validate_graph(Graph(nodes=[a, b], edges=edges), NODE_TYPES)

    assert [v.code for v in violations] == ["cycle"]


def test_self_loop_is_rejected_as_cycle() -> None:
    a = make_node("relay")
    edges = [Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=a.id, to_port="in")]

    violations = validate_graph(Graph(nodes=[a], edges=edges), NODE_TYPES)

    assert [v.code for v in violations] == ["cycle"]


def test_edge_to_unknown_node_is_rejected() -> None:
    a = make_node("source")
    edges = [Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=uuid4(), to_port="in")]

    violations = validate_graph(Graph(nodes=[a], edges=edges), NODE_TYPES)

    assert [v.code for v in violations] == ["unknown_node"]


def test_diamond_graph_is_valid() -> None:
    a, b, c, d = (
        make_node("source"),
        make_node("relay_multi"),
        make_node("relay_multi"),
        make_node("sink_multi"),
    )
    edges = [
        Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=b.id, to_port="in"),
        Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=c.id, to_port="in"),
        Edge(id=uuid4(), from_node=b.id, from_port="out", to_node=d.id, to_port="in"),
        Edge(id=uuid4(), from_node=c.id, from_port="out", to_node=d.id, to_port="in"),
    ]

    assert validate_graph(Graph(nodes=[a, b, c, d], edges=edges), NODE_TYPES) == []


def test_reports_all_unknown_node_violations_not_just_the_first() -> None:
    a, b = make_node("source"), make_node("sink")
    edges = [
        Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=uuid4(), to_port="in"),
        Edge(id=uuid4(), from_node=uuid4(), from_port="out", to_node=b.id, to_port="in"),
    ]

    violations = validate_graph(Graph(nodes=[a, b], edges=edges), NODE_TYPES)

    assert len(violations) == 2


def test_unknown_node_type_is_rejected() -> None:
    a = make_node("does_not_exist")

    violations = validate_graph(Graph(nodes=[a], edges=[]), NODE_TYPES)

    assert [v.code for v in violations] == ["unknown_node_type"]


def test_unknown_port_is_rejected() -> None:
    a, b = make_node("source"), make_node("sink")
    edges = [Edge(id=uuid4(), from_node=a.id, from_port="nope", to_node=b.id, to_port="in")]

    violations = validate_graph(Graph(nodes=[a, b], edges=edges), NODE_TYPES)

    assert [v.code for v in violations] == ["unknown_port"]


def test_incompatible_port_kind_is_rejected() -> None:
    a, b = make_node("source"), make_node("sink_json")
    edges = [Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=b.id, to_port="in")]

    violations = validate_graph(Graph(nodes=[a, b], edges=edges), NODE_TYPES)

    assert [v.code for v in violations] == ["incompatible_port"]


def test_duplicate_connection_to_non_multiple_input_is_rejected() -> None:
    a1, a2, b = make_node("source"), make_node("source"), make_node("sink")
    edges = [
        Edge(id=uuid4(), from_node=a1.id, from_port="out", to_node=b.id, to_port="in"),
        Edge(id=uuid4(), from_node=a2.id, from_port="out", to_node=b.id, to_port="in"),
    ]

    violations = validate_graph(Graph(nodes=[a1, a2, b], edges=edges), NODE_TYPES)

    assert [v.code for v in violations] == ["port_not_multiple"]


def test_duplicate_connection_to_multiple_input_is_allowed() -> None:
    a1, a2, b = make_node("source"), make_node("source"), make_node("sink_multi")
    edges = [
        Edge(id=uuid4(), from_node=a1.id, from_port="out", to_node=b.id, to_port="in"),
        Edge(id=uuid4(), from_node=a2.id, from_port="out", to_node=b.id, to_port="in"),
    ]

    assert validate_graph(Graph(nodes=[a1, a2, b], edges=edges), NODE_TYPES) == []


def test_missing_required_input_is_rejected() -> None:
    b = make_node("sink")

    violations = validate_graph(Graph(nodes=[b], edges=[]), NODE_TYPES)

    assert [v.code for v in violations] == ["missing_required_input"]


def test_missing_output_node_is_rejected() -> None:
    a = make_node("source")

    violations = validate_graph(Graph(nodes=[a], edges=[]), NODE_TYPES)

    assert [v.code for v in violations] == ["missing_output_node"]
