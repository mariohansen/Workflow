from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Index, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, CreatedAtMixin, pg_enum
from app.domain.ids import new_id
from app.domain.runs import StepRunStatus, WorkflowRunStatus


class WorkflowRun(CreatedAtMixin, Base):
    __tablename__ = "workflow_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    workflow_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflow_versions.id"), index=True
    )
    status: Mapped[WorkflowRunStatus] = mapped_column(
        pg_enum(WorkflowRunStatus), default=WorkflowRunStatus.PENDING
    )
    started_at: Mapped[datetime | None]
    finished_at: Mapped[datetime | None]


class StepRun(CreatedAtMixin, Base):
    __tablename__ = "step_runs"
    __table_args__ = (
        UniqueConstraint("run_id", "node_id", "attempt"),
        Index("ix_step_runs_run_id_status", "run_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflow_runs.id"))
    node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflow_nodes.id"))
    attempt: Mapped[int] = mapped_column(default=1)
    status: Mapped[StepRunStatus] = mapped_column(
        pg_enum(StepRunStatus), default=StepRunStatus.PENDING
    )

    # pinned at dispatch time for prompt nodes, so a run stays reproducible later
    prompt_version_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("prompt_versions.id"))
    provider: Mapped[str | None]
    model: Mapped[str | None]
    parameters: Mapped[dict[str, object] | None] = mapped_column(JSONB)

    started_at: Mapped[datetime | None]
    finished_at: Mapped[datetime | None]
    error: Mapped[str | None] = mapped_column(Text)
