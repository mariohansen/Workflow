from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from app.domain.runs import StepRunStatus, WorkflowRunStatus
from app.runs.service import RunView


class StepRunDto(BaseModel):
    node_id: UUID
    status: StepRunStatus
    error: str | None


class RunResponse(BaseModel):
    id: UUID
    status: WorkflowRunStatus
    steps: list[StepRunDto]

    @classmethod
    def from_domain(cls, run: RunView) -> RunResponse:
        return cls(
            id=run.id,
            status=run.status,
            steps=[
                StepRunDto(node_id=s.node_id, status=s.status, error=s.error) for s in run.steps
            ],
        )
