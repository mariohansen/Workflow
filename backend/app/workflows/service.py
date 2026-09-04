from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.workflows import Workflow as WorkflowRow
from app.db.models.workflows import WorkflowEdge as WorkflowEdgeRow
from app.db.models.workflows import WorkflowNode as WorkflowNodeRow
from app.db.models.workflows import WorkflowVersion as WorkflowVersionRow
from app.db.repositories.workflows import (
    WorkflowEdgeRepository,
    WorkflowNodeRepository,
    WorkflowRepository,
    WorkflowVersionRepository,
)
from app.domain.errors import WorkflowNotFoundError, WorkflowValidationError
from app.domain.graph import Edge, Graph, Node, Position, validate_graph
from app.domain.ids import new_id


@dataclass(frozen=True)
class WorkflowVersionView:
    id: UUID
    version: int
    graph: Graph


class WorkflowService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._workflows = WorkflowRepository(session)
        self._versions = WorkflowVersionRepository(session)
        self._nodes = WorkflowNodeRepository(session)
        self._edges = WorkflowEdgeRepository(session)

    async def create_workflow(self, name: str) -> WorkflowRow:
        workflow = WorkflowRow(id=new_id(), name=name)
        self._workflows.add(workflow)
        await self._session.commit()
        return workflow

    async def list_workflows(self) -> list[WorkflowRow]:
        return await self._workflows.list_all()

    async def get_latest_version(self, workflow_id: UUID) -> WorkflowVersionView | None:
        workflow = await self._workflows.get(workflow_id)
        if workflow is None:
            raise WorkflowNotFoundError(workflow_id)

        version = await self._versions.latest_for_workflow(workflow_id)
        if version is None:
            return None

        nodes = await self._nodes.for_version(version.id)
        edges = await self._edges.for_version(version.id)
        return WorkflowVersionView(
            id=version.id, version=version.version, graph=_to_domain_graph(nodes, edges)
        )

    async def save_version(self, workflow_id: UUID, graph: Graph) -> WorkflowVersionView:
        workflow = await self._workflows.get(workflow_id)
        if workflow is None:
            raise WorkflowNotFoundError(workflow_id)

        violations = validate_graph(graph)
        if violations:
            raise WorkflowValidationError(violations)

        version_row = WorkflowVersionRow(
            id=new_id(),
            workflow_id=workflow_id,
            version=await self._versions.next_version_number(workflow_id),
        )
        self._versions.add(version_row)
        await self._session.flush()

        id_map, persisted_nodes = _persist_nodes(self._nodes, version_row.id, graph.nodes)
        await self._session.flush()
        persisted_edges = _persist_edges(self._edges, version_row.id, graph.edges, id_map)
        await self._session.commit()

        persisted = Graph(nodes=persisted_nodes, edges=persisted_edges)
        return WorkflowVersionView(id=version_row.id, version=version_row.version, graph=persisted)


def _to_domain_graph(nodes: list[WorkflowNodeRow], edges: list[WorkflowEdgeRow]) -> Graph:
    return Graph(
        nodes=[
            Node(
                id=n.id, type=n.type, position=Position(n.position_x, n.position_y), config=n.config
            )
            for n in nodes
        ],
        edges=[
            Edge(
                id=e.id,
                from_node=e.from_node_id,
                from_port=e.from_port,
                to_node=e.to_node_id,
                to_port=e.to_port,
            )
            for e in edges
        ],
    )


def _persist_nodes(
    nodes: WorkflowNodeRepository,
    version_id: UUID,
    domain_nodes: Sequence[Node],
) -> tuple[dict[UUID, UUID], list[Node]]:
    """Re-mints ids for every node: a version is an immutable, self-contained
    snapshot, so client-supplied ids from a previous load must never collide with it."""
    id_map: dict[UUID, UUID] = {}
    persisted: list[Node] = []
    for node in domain_nodes:
        row_id = new_id()
        id_map[node.id] = row_id
        nodes.add(
            WorkflowNodeRow(
                id=row_id,
                workflow_version_id=version_id,
                type=node.type,
                position_x=node.position.x,
                position_y=node.position.y,
                config=dict(node.config),
            )
        )
        persisted.append(
            Node(id=row_id, type=node.type, position=node.position, config=node.config)
        )

    return id_map, persisted


def _persist_edges(
    edges: WorkflowEdgeRepository,
    version_id: UUID,
    domain_edges: Sequence[Edge],
    id_map: dict[UUID, UUID],
) -> list[Edge]:
    """Requires the referenced nodes to already be flushed to the database:
    SQLAlchemy only orders inserts by foreign keys between mapped `relationship()`s,
    and these rows are linked by bare id columns instead."""
    persisted: list[Edge] = []
    for edge in domain_edges:
        row_id = new_id()
        from_id, to_id = id_map[edge.from_node], id_map[edge.to_node]
        edges.add(
            WorkflowEdgeRow(
                id=row_id,
                workflow_version_id=version_id,
                from_node_id=from_id,
                from_port=edge.from_port,
                to_node_id=to_id,
                to_port=edge.to_port,
            )
        )
        persisted.append(
            Edge(
                id=row_id,
                from_node=from_id,
                from_port=edge.from_port,
                to_node=to_id,
                to_port=edge.to_port,
            )
        )

    return persisted
