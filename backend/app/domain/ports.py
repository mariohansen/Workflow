from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from app.domain.artifacts import ArtifactKind


@dataclass(frozen=True)
class InputPort:
    name: str
    label: str
    accepts: frozenset[ArtifactKind]
    required: bool = True
    multiple: bool = False


@dataclass(frozen=True)
class OutputPort:
    name: str
    label: str
    produces: ArtifactKind


@dataclass(frozen=True)
class NodeType:
    type: str
    label: str
    category: str
    icon: str = ""
    inputs: tuple[InputPort, ...] = ()
    outputs: tuple[OutputPort, ...] = ()
    config_schema: Mapping[str, Any] = field(default_factory=dict)
