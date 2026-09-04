from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, CreatedAtMixin
from app.domain.ids import new_id


class Workflow(CreatedAtMixin, Base):
    __tablename__ = "workflows"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    name: Mapped[str]


class WorkflowVersion(CreatedAtMixin, Base):
    """Append-only: a saved change to a workflow is a new version, never an update."""

    __tablename__ = "workflow_versions"
    __table_args__ = (UniqueConstraint("workflow_id", "version"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    workflow_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflows.id"), index=True)
    version: Mapped[int]


class WorkflowNode(Base):
    __tablename__ = "workflow_nodes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    workflow_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflow_versions.id"), index=True
    )
    type: Mapped[str]  # step type name, not an enum - new types must not require a migration
    position_x: Mapped[float] = mapped_column(Float)
    position_y: Mapped[float] = mapped_column(Float)
    config: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict)


class WorkflowEdge(Base):
    __tablename__ = "workflow_edges"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    workflow_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflow_versions.id"), index=True
    )
    from_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflow_nodes.id"))
    from_port: Mapped[str]
    to_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflow_nodes.id"))
    to_port: Mapped[str]
