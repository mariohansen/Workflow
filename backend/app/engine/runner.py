from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.domain.artifacts import Artifact
from app.domain.graph import Graph
from app.engine.executor import Completed, Failed, StepContext, StepResult, Suspended
from app.engine.planner import downstream_nodes, ready_nodes

ExecuteStep = Callable[[UUID, StepContext], Awaitable[StepResult]]


@dataclass(frozen=True)
class RunOutcome:
    completed: frozenset[UUID]
    failed: frozenset[UUID]
    skipped: frozenset[UUID]
    suspended: UUID | None
    artifacts: Mapping[UUID, Sequence[Artifact]]


async def run_graph(
    run_id: UUID,
    graph: Graph,
    node_configs: Mapping[UUID, Mapping[str, Any]],
    execute_step: ExecuteStep,
) -> RunOutcome:
    """Runs every ready node to completion, suspension, or exhaustion of the
    ready-set. A failed node marks its dependents SKIPPED; independent
    branches keep going. Stops at the first suspension - resuming a run is
    a separate concern, not handled here."""
    completed: set[UUID] = set()
    failed: set[UUID] = set()
    skipped: set[UUID] = set()
    suspended: UUID | None = None
    artifacts: dict[UUID, Sequence[Artifact]] = {}

    while suspended is None:
        blocked = failed | skipped
        ready = [
            node_id
            for node_id in ready_nodes(graph, frozenset(completed))
            if node_id not in blocked
        ]
        if not ready:
            break

        for node_id in ready:
            context = StepContext(
                run_id=run_id,
                node_id=node_id,
                config=node_configs.get(node_id, {}),
                inputs=_resolve_inputs(graph, node_id, artifacts),
            )
            result = await execute_step(node_id, context)

            if isinstance(result, Completed):
                completed.add(node_id)
                artifacts[node_id] = result.artifacts
            elif isinstance(result, Failed):
                failed.add(node_id)
                skipped |= downstream_nodes(graph, node_id) - completed - failed
            elif isinstance(result, Suspended):
                suspended = node_id
                break

    return RunOutcome(
        completed=frozenset(completed),
        failed=frozenset(failed),
        skipped=frozenset(skipped),
        suspended=suspended,
        artifacts=artifacts,
    )


def _resolve_inputs(
    graph: Graph, node_id: UUID, artifacts: Mapping[UUID, Sequence[Artifact]]
) -> dict[str, list[Artifact]]:
    """Every artifact a predecessor produced goes to the edge's target port.
    Correct as long as a node type has at most one output port - revisit once
    a step produces more than one, since Completed doesn't tag which port an
    artifact came from."""
    inputs: dict[str, list[Artifact]] = {}
    for edge in graph.edges:
        if edge.to_node != node_id:
            continue
        inputs.setdefault(edge.to_port, []).extend(artifacts.get(edge.from_node, []))
    return inputs
