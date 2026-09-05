from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.runs import StepRun, WorkflowRun


class WorkflowRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, run: WorkflowRun) -> None:
        self._session.add(run)

    async def get(self, run_id: UUID) -> WorkflowRun | None:
        return await self._session.get(WorkflowRun, run_id)


class StepRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, step_run: StepRun) -> None:
        self._session.add(step_run)

    async def for_run(self, run_id: UUID) -> list[StepRun]:
        result = await self._session.execute(select(StepRun).where(StepRun.run_id == run_id))
        return list(result.scalars().all())
