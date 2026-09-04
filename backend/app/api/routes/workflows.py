from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.schemas.workflows import (
    GraphDto,
    WorkflowCreateRequest,
    WorkflowResponse,
    WorkflowVersionResponse,
)
from app.container import get_workflow_service
from app.workflows.service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workflow(
    request: WorkflowCreateRequest,
    service: WorkflowService = Depends(get_workflow_service),
) -> WorkflowResponse:
    workflow = await service.create_workflow(request.name)
    return WorkflowResponse(id=workflow.id, name=workflow.name)


@router.get("")
async def list_workflows(
    service: WorkflowService = Depends(get_workflow_service),
) -> list[WorkflowResponse]:
    workflows = await service.list_workflows()
    return [WorkflowResponse(id=w.id, name=w.name) for w in workflows]


@router.get("/{workflow_id}/versions/latest")
async def get_latest_version(
    workflow_id: UUID,
    service: WorkflowService = Depends(get_workflow_service),
) -> WorkflowVersionResponse | None:
    version = await service.get_latest_version(workflow_id)
    if version is None:
        return None
    return WorkflowVersionResponse(
        id=version.id, version=version.version, graph=GraphDto.from_domain(version.graph)
    )


@router.post("/{workflow_id}/versions", status_code=status.HTTP_201_CREATED)
async def save_version(
    workflow_id: UUID,
    graph: GraphDto,
    service: WorkflowService = Depends(get_workflow_service),
) -> WorkflowVersionResponse:
    version = await service.save_version(workflow_id, graph.to_domain())
    return WorkflowVersionResponse(
        id=version.id, version=version.version, graph=GraphDto.from_domain(version.graph)
    )
