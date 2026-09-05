from __future__ import annotations

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.domain.clock import Clock, SystemClock
from app.engine.registry import StepRegistry
from app.runs.service import RunService
from app.steps import build_step_registry
from app.workflows.service import WorkflowService


@lru_cache
def get_step_registry() -> StepRegistry:
    return build_step_registry()


@lru_cache
def get_clock() -> Clock:
    return SystemClock()


async def get_workflow_service(
    session: AsyncSession = Depends(get_session),
    registry: StepRegistry = Depends(get_step_registry),
) -> WorkflowService:
    return WorkflowService(session, registry.node_types())


async def get_run_service(
    session: AsyncSession = Depends(get_session),
    registry: StepRegistry = Depends(get_step_registry),
    clock: Clock = Depends(get_clock),
) -> RunService:
    return RunService(session, registry, clock)
