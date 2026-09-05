from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.schemas.node_types import NodeTypeDto
from app.container import get_step_registry
from app.engine.registry import StepRegistry

router = APIRouter(tags=["node-types"])


@router.get("/node-types")
async def list_node_types(
    registry: StepRegistry = Depends(get_step_registry),
) -> list[NodeTypeDto]:
    return [NodeTypeDto.from_domain(node_type) for node_type in registry.node_types().values()]
