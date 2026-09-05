from __future__ import annotations

from app.domain.artifacts import ArtifactKind
from app.domain.ports import InputPort, NodeType
from app.engine.executor import Completed, StepContext, StepExecutor, StepResult


class OutputStepExecutor(StepExecutor):
    @property
    def descriptor(self) -> NodeType:
        return NodeType(
            type="output",
            label="Output",
            category="output",
            inputs=(InputPort("value", "Value", frozenset(ArtifactKind)),),
        )

    async def execute(self, context: StepContext) -> StepResult:
        return Completed(artifacts=list(context.inputs.get("value", [])))
