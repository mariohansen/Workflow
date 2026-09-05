from __future__ import annotations

from app.domain.errors import DomainError
from app.domain.ports import NodeType
from app.engine.executor import StepExecutor


class UnknownStepTypeError(DomainError):
    code = "unknown_step_type"

    def __init__(self, step_type: str) -> None:
        self.step_type = step_type
        super().__init__(f"no step executor registered for type {step_type!r}")


class StepRegistry:
    def __init__(self, executors: tuple[StepExecutor, ...] = ()) -> None:
        self._executors = {executor.descriptor.type: executor for executor in executors}

    def get(self, step_type: str) -> StepExecutor:
        executor = self._executors.get(step_type)
        if executor is None:
            raise UnknownStepTypeError(step_type)
        return executor

    def node_types(self) -> dict[str, NodeType]:
        return {step_type: executor.descriptor for step_type, executor in self._executors.items()}
