from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.artifacts import Artifact as ArtifactRow
from app.db.models.runs import StepRun as StepRunRow
from app.db.models.runs import WorkflowRun as WorkflowRunRow
from app.db.repositories.artifacts import ArtifactRepository
from app.db.repositories.runs import StepRunRepository, WorkflowRunRepository
from app.db.repositories.workflows import (
    WorkflowEdgeRepository,
    WorkflowNodeRepository,
    WorkflowRepository,
    WorkflowVersionRepository,
    load_graph,
)
from app.domain.artifacts import Artifact, ArtifactKind, TextArtifact
from app.domain.clock import Clock
from app.domain.errors import (
    NoWorkflowVersionError,
    RunNotFoundError,
    WorkflowNotFoundError,
    WorkflowValidationError,
)
from app.domain.graph import validate_graph
from app.domain.ids import new_id
from app.domain.runs import StepRunStatus, WorkflowRunStatus
from app.engine.executor import Completed, Failed, StepContext, StepResult, Suspended
from app.engine.registry import StepRegistry
from app.engine.runner import RunOutcome, run_graph


@dataclass(frozen=True)
class StepRunView:
    node_id: UUID
    status: StepRunStatus
    error: str | None


@dataclass(frozen=True)
class RunView:
    id: UUID
    status: WorkflowRunStatus
    steps: list[StepRunView]


class RunService:
    def __init__(self, session: AsyncSession, registry: StepRegistry, clock: Clock) -> None:
        self._session = session
        self._registry = registry
        self._clock = clock
        self._workflows = WorkflowRepository(session)
        self._versions = WorkflowVersionRepository(session)
        self._nodes = WorkflowNodeRepository(session)
        self._edges = WorkflowEdgeRepository(session)
        self._runs = WorkflowRunRepository(session)
        self._step_runs = StepRunRepository(session)
        self._artifacts = ArtifactRepository(session)

    async def start_run(self, workflow_id: UUID) -> RunView:
        workflow = await self._workflows.get(workflow_id)
        if workflow is None:
            raise WorkflowNotFoundError(workflow_id)

        version = await self._versions.latest_for_workflow(workflow_id)
        if version is None:
            raise NoWorkflowVersionError(workflow_id)

        node_rows = await self._nodes.for_version(version.id)
        edge_rows = await self._edges.for_version(version.id)
        graph = load_graph(node_rows, edge_rows)
        node_type_by_id = {node.id: node.type for node in graph.nodes}

        violations = validate_graph(graph, self._registry.node_types())
        if violations:
            raise WorkflowValidationError(violations)

        run_row = WorkflowRunRow(
            id=new_id(),
            workflow_version_id=version.id,
            status=WorkflowRunStatus.RUNNING,
            started_at=self._clock.now(),
        )
        self._runs.add(run_row)
        await self._session.flush()

        step_statuses: dict[UUID, StepRunStatus] = {}
        errors: dict[UUID, str] = {}

        async def execute_step(node_id: UUID, context: StepContext) -> StepResult:
            step_run_row = StepRunRow(
                id=new_id(),
                run_id=run_row.id,
                node_id=node_id,
                attempt=1,
                status=StepRunStatus.RUNNING,
                started_at=self._clock.now(),
            )
            self._step_runs.add(step_run_row)
            await self._session.flush()

            executor = self._registry.get(node_type_by_id[node_id])
            result = await executor.execute(context)
            step_run_row.finished_at = self._clock.now()

            if isinstance(result, Completed):
                step_run_row.status = StepRunStatus.COMPLETED
                for artifact in result.artifacts:
                    self._artifacts.add(_to_artifact_row(artifact, step_run_row.id))
            elif isinstance(result, Failed):
                step_run_row.status = StepRunStatus.FAILED
                step_run_row.error = result.error
                errors[node_id] = result.error
            elif isinstance(result, Suspended):
                step_run_row.status = StepRunStatus.WAITING_FOR_INPUT

            step_statuses[node_id] = step_run_row.status
            await self._session.flush()
            return result

        outcome = await run_graph(
            run_row.id, graph, {node.id: node.config for node in graph.nodes}, execute_step
        )

        for node_id in outcome.skipped:
            self._step_runs.add(
                StepRunRow(
                    id=new_id(),
                    run_id=run_row.id,
                    node_id=node_id,
                    attempt=1,
                    status=StepRunStatus.SKIPPED,
                )
            )
            step_statuses[node_id] = StepRunStatus.SKIPPED

        run_row.status = _final_run_status(outcome)
        if run_row.status in (WorkflowRunStatus.COMPLETED, WorkflowRunStatus.FAILED):
            run_row.finished_at = self._clock.now()
        await self._session.commit()

        return RunView(
            id=run_row.id,
            status=run_row.status,
            steps=[
                StepRunView(node_id=node_id, status=status, error=errors.get(node_id))
                for node_id, status in step_statuses.items()
            ],
        )

    async def get_run(self, run_id: UUID) -> RunView:
        run = await self._runs.get(run_id)
        if run is None:
            raise RunNotFoundError(run_id)

        step_rows = await self._step_runs.for_run(run_id)
        return RunView(
            id=run.id,
            status=run.status,
            steps=[
                StepRunView(node_id=s.node_id, status=s.status, error=s.error) for s in step_rows
            ],
        )


def _to_artifact_row(artifact: Artifact, step_run_id: UUID) -> ArtifactRow:
    if isinstance(artifact, TextArtifact):
        return ArtifactRow(
            id=new_id(),
            kind=ArtifactKind.TEXT,
            produced_by_step_run_id=step_run_id,
            text=artifact.text,
        )
    raise TypeError(f"unsupported artifact type: {type(artifact)!r}")


def _final_run_status(outcome: RunOutcome) -> WorkflowRunStatus:
    if outcome.suspended is not None:
        return WorkflowRunStatus.WAITING_FOR_INPUT
    if outcome.failed:
        return WorkflowRunStatus.FAILED
    return WorkflowRunStatus.COMPLETED
