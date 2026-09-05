from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.domain.artifacts import Artifact
from app.domain.ports import NodeType


@dataclass(frozen=True)
class StepContext:
    run_id: UUID
    node_id: UUID
    config: Mapping[str, Any]
    inputs: Mapping[str, Sequence[Artifact]]


@dataclass(frozen=True)
class Completed:
    artifacts: Sequence[Artifact]


@dataclass(frozen=True)
class Suspended:
    reason: str
    payload: Mapping[str, Any]


@dataclass(frozen=True)
class Failed:
    error: str
    retryable: bool = False


StepResult = Completed | Suspended | Failed


class StepExecutor(ABC):
    @property
    @abstractmethod
    def descriptor(self) -> NodeType: ...

    @abstractmethod
    async def execute(self, context: StepContext) -> StepResult: ...
