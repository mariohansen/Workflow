from __future__ import annotations

from uuid import uuid4

import pytest

from app.domain.artifacts import TextArtifact
from app.engine.executor import Completed, StepContext
from app.steps.output import OutputStepExecutor


@pytest.mark.asyncio
async def test_passes_through_the_value_input() -> None:
    executor = OutputStepExecutor()
    artifact = TextArtifact(text="hi")
    context = StepContext(run_id=uuid4(), node_id=uuid4(), config={}, inputs={"value": [artifact]})

    result = await executor.execute(context)

    assert result == Completed(artifacts=[artifact])


@pytest.mark.asyncio
async def test_empty_when_no_input_connected() -> None:
    executor = OutputStepExecutor()
    context = StepContext(run_id=uuid4(), node_id=uuid4(), config={}, inputs={})

    result = await executor.execute(context)

    assert result == Completed(artifacts=[])
