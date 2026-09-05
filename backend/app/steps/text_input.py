from __future__ import annotations

from app.domain.artifacts import ArtifactKind, TextArtifact
from app.domain.ports import NodeType, OutputPort
from app.engine.executor import Completed, StepContext, StepExecutor, StepResult


class TextInputStepExecutor(StepExecutor):
    @property
    def descriptor(self) -> NodeType:
        return NodeType(
            type="text_input",
            label="Text Input",
            category="input",
            outputs=(OutputPort("text", "Text", ArtifactKind.TEXT),),
            config_schema={
                "type": "object",
                "properties": {"value": {"type": "string"}},
                "required": ["value"],
            },
        )

    async def execute(self, context: StepContext) -> StepResult:
        value = context.config.get("value", "")
        return Completed(artifacts=[TextArtifact(text=str(value))])
