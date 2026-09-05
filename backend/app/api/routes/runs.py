from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.schemas.runs import RunResponse
from app.container import get_run_service
from app.runs.service import RunService

router = APIRouter(tags=["runs"])


@router.post("/workflows/{workflow_id}/runs", status_code=status.HTTP_201_CREATED)
async def start_run(
    workflow_id: UUID,
    service: RunService = Depends(get_run_service),
) -> RunResponse:
    run = await service.start_run(workflow_id)
    return RunResponse.from_domain(run)


@router.get("/runs/{run_id}")
async def get_run(
    run_id: UUID,
    service: RunService = Depends(get_run_service),
) -> RunResponse:
    run = await service.get_run(run_id)
    return RunResponse.from_domain(run)
