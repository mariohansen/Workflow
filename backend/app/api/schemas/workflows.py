from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.domain.graph import Edge, Graph, Node, Position


class PositionDto(BaseModel):
    x: float
    y: float


class NodeDto(BaseModel):
    id: UUID
    type: str
    position: PositionDto
    config: dict[str, Any] = {}

    def to_domain(self) -> Node:
        return Node(
            id=self.id,
            type=self.type,
            position=Position(self.position.x, self.position.y),
            config=self.config,
        )

    @classmethod
    def from_domain(cls, node: Node) -> NodeDto:
        return cls(
            id=node.id,
            type=node.type,
            position=PositionDto(x=node.position.x, y=node.position.y),
            config=dict(node.config),
        )


class EdgeDto(BaseModel):
    id: UUID
    from_node: UUID
    from_port: str
    to_node: UUID
    to_port: str

    def to_domain(self) -> Edge:
        return Edge(
            id=self.id,
            from_node=self.from_node,
            from_port=self.from_port,
            to_node=self.to_node,
            to_port=self.to_port,
        )

    @classmethod
    def from_domain(cls, edge: Edge) -> EdgeDto:
        return cls(
            id=edge.id,
            from_node=edge.from_node,
            from_port=edge.from_port,
            to_node=edge.to_node,
            to_port=edge.to_port,
        )


class GraphDto(BaseModel):
    nodes: list[NodeDto]
    edges: list[EdgeDto]

    def to_domain(self) -> Graph:
        return Graph(
            nodes=[node.to_domain() for node in self.nodes],
            edges=[edge.to_domain() for edge in self.edges],
        )

    @classmethod
    def from_domain(cls, graph: Graph) -> GraphDto:
        return cls(
            nodes=[NodeDto.from_domain(node) for node in graph.nodes],
            edges=[EdgeDto.from_domain(edge) for edge in graph.edges],
        )


class WorkflowCreateRequest(BaseModel):
    name: str


class WorkflowResponse(BaseModel):
    id: UUID
    name: str


class WorkflowVersionResponse(BaseModel):
    id: UUID
    version: int
    graph: GraphDto
