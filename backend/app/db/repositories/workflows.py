from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.workflows import Workflow, WorkflowEdge, WorkflowNode, WorkflowVersion
from app.domain.graph import Edge, Graph, Node, Position


def load_graph(node_rows: list[WorkflowNode], edge_rows: list[WorkflowEdge]) -> Graph:
    return Graph(
        nodes=[
            Node(
                id=n.id, type=n.type, position=Position(n.position_x, n.position_y), config=n.config
            )
            for n in node_rows
        ],
        edges=[
            Edge(
                id=e.id,
                from_node=e.from_node_id,
                from_port=e.from_port,
                to_node=e.to_node_id,
                to_port=e.to_port,
            )
            for e in edge_rows
        ],
    )


class WorkflowRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, workflow: Workflow) -> None:
        self._session.add(workflow)

    async def get(self, workflow_id: UUID) -> Workflow | None:
        return await self._session.get(Workflow, workflow_id)

    async def list_all(self) -> list[Workflow]:
        result = await self._session.execute(select(Workflow).order_by(Workflow.created_at))
        return list(result.scalars().all())


class WorkflowVersionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, version: WorkflowVersion) -> None:
        self._session.add(version)

    async def latest_for_workflow(self, workflow_id: UUID) -> WorkflowVersion | None:
        result = await self._session.execute(
            select(WorkflowVersion)
            .where(WorkflowVersion.workflow_id == workflow_id)
            .order_by(WorkflowVersion.version.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def next_version_number(self, workflow_id: UUID) -> int:
        latest = await self.latest_for_workflow(workflow_id)
        return 1 if latest is None else latest.version + 1


class WorkflowNodeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, node: WorkflowNode) -> None:
        self._session.add(node)

    async def for_version(self, workflow_version_id: UUID) -> list[WorkflowNode]:
        result = await self._session.execute(
            select(WorkflowNode).where(WorkflowNode.workflow_version_id == workflow_version_id)
        )
        return list(result.scalars().all())


class WorkflowEdgeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, edge: WorkflowEdge) -> None:
        self._session.add(edge)

    async def for_version(self, workflow_version_id: UUID) -> list[WorkflowEdge]:
        result = await self._session.execute(
            select(WorkflowEdge).where(WorkflowEdge.workflow_version_id == workflow_version_id)
        )
        return list(result.scalars().all())
