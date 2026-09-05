from __future__ import annotations

from uuid import uuid4

import pytest

from app.domain.artifacts import TextArtifact
from app.domain.graph import Edge, Graph, Node, Position
from app.engine.executor import Completed, Failed, StepContext, StepResult, Suspended
from app.engine.runner import run_graph


def make_node() -> Node:
    return Node(id=uuid4(), type="relay", position=Position(0, 0), config={})


@pytest.mark.asyncio
async def test_runs_independent_nodes_to_completion() -> None:
    a, b = make_node(), make_node()
    graph = Graph(nodes=[a, b], edges=[])
    called: set[object] = set()

    async def execute(node_id: object, context: StepContext) -> StepResult:
        called.add(node_id)
        return Completed(artifacts=[])

    outcome = await run_graph(uuid4(), graph, {}, execute)

    assert outcome.completed == frozenset({a.id, b.id})
    assert called == {a.id, b.id}


@pytest.mark.asyncio
async def test_propagates_artifacts_along_an_edge() -> None:
    a, b = make_node(), make_node()
    edges = [Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=b.id, to_port="in")]
    graph = Graph(nodes=[a, b], edges=edges)

    async def execute(node_id: object, context: StepContext) -> StepResult:
        if node_id == a.id:
            return Completed(artifacts=[TextArtifact("hello")])
        assert context.inputs["in"] == [TextArtifact("hello")]
        return Completed(artifacts=[])

    outcome = await run_graph(uuid4(), graph, {}, execute)

    assert outcome.completed == frozenset({a.id, b.id})


@pytest.mark.asyncio
async def test_node_config_is_passed_into_its_context() -> None:
    a = make_node()
    graph = Graph(nodes=[a], edges=[])
    seen_config: dict[str, object] = {}

    async def execute(node_id: object, context: StepContext) -> StepResult:
        seen_config.update(context.config)
        return Completed(artifacts=[])

    await run_graph(uuid4(), graph, {a.id: {"value": "hi"}}, execute)

    assert seen_config == {"value": "hi"}


@pytest.mark.asyncio
async def test_failure_skips_downstream_but_not_independent_branch() -> None:
    a, b, c = make_node(), make_node(), make_node()
    edges = [Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=b.id, to_port="in")]
    graph = Graph(nodes=[a, b, c], edges=edges)

    async def execute(node_id: object, context: StepContext) -> StepResult:
        if node_id == a.id:
            return Failed(error="boom")
        return Completed(artifacts=[])

    outcome = await run_graph(uuid4(), graph, {}, execute)

    assert outcome.failed == frozenset({a.id})
    assert outcome.skipped == frozenset({b.id})
    assert outcome.completed == frozenset({c.id})


@pytest.mark.asyncio
async def test_suspension_stops_the_run_before_downstream_nodes() -> None:
    a, b = make_node(), make_node()
    edges = [Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=b.id, to_port="in")]
    graph = Graph(nodes=[a, b], edges=edges)

    async def execute(node_id: object, context: StepContext) -> StepResult:
        return Suspended(reason="waiting_for_input", payload={})

    outcome = await run_graph(uuid4(), graph, {}, execute)

    assert outcome.suspended == a.id
    assert outcome.completed == frozenset()
    assert outcome.failed == frozenset()
    assert outcome.skipped == frozenset()


@pytest.mark.asyncio
async def test_parallel_branches_both_run_before_a_shared_successor() -> None:
    a, b, c = make_node(), make_node(), make_node()
    edges = [
        Edge(id=uuid4(), from_node=a.id, from_port="out", to_node=c.id, to_port="a"),
        Edge(id=uuid4(), from_node=b.id, from_port="out", to_node=c.id, to_port="b"),
    ]
    graph = Graph(nodes=[a, b, c], edges=edges)
    order: list[object] = []

    async def execute(node_id: object, context: StepContext) -> StepResult:
        order.append(node_id)
        return Completed(artifacts=[])

    outcome = await run_graph(uuid4(), graph, {}, execute)

    assert outcome.completed == frozenset({a.id, b.id, c.id})
    assert order.index(c.id) > order.index(a.id)
    assert order.index(c.id) > order.index(b.id)
