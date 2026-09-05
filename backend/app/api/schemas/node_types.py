from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.domain.artifacts import ArtifactKind
from app.domain.ports import InputPort, NodeType, OutputPort


class InputPortDto(BaseModel):
    name: str
    label: str
    accepts: list[ArtifactKind]
    required: bool
    multiple: bool

    @classmethod
    def from_domain(cls, port: InputPort) -> InputPortDto:
        return cls(
            name=port.name,
            label=port.label,
            accepts=sorted(port.accepts),
            required=port.required,
            multiple=port.multiple,
        )


class OutputPortDto(BaseModel):
    name: str
    label: str
    produces: ArtifactKind

    @classmethod
    def from_domain(cls, port: OutputPort) -> OutputPortDto:
        return cls(name=port.name, label=port.label, produces=port.produces)


class NodeTypeDto(BaseModel):
    type: str
    label: str
    category: str
    icon: str
    inputs: list[InputPortDto]
    outputs: list[OutputPortDto]
    config_schema: dict[str, Any]

    @classmethod
    def from_domain(cls, node_type: NodeType) -> NodeTypeDto:
        return cls(
            type=node_type.type,
            label=node_type.label,
            category=node_type.category,
            icon=node_type.icon,
            inputs=[InputPortDto.from_domain(p) for p in node_type.inputs],
            outputs=[OutputPortDto.from_domain(p) for p in node_type.outputs],
            config_schema=dict(node_type.config_schema),
        )
