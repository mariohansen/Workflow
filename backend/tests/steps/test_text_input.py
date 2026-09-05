from __future__ import annotations

from uuid import uuid4

import pytest

from app.domain.artifacts import TextArtifact
from app.engine.executor import Completed, StepContext
from app.steps.text_input import TextInputStepExecutor


@pytest.mark.asyncio
async def test_produces_text_artifact_from_config() -> None:
    executor = TextInputStepExecutor()
    context = StepContext(run_id=uuid4(), node_id=uuid4(), config={"value": "hello"}, inputs={})

    result = await executor.execute(context)

    assert result == Completed(artifacts=[TextArtifact(text="hello")])


@pytest.mark.asyncio
async def test_defaults_to_empty_string_when_value_missing() -> None:
    executor = TextInputStepExecutor()
    context = StepContext(run_id=uuid4(), node_id=uuid4(), config={}, inputs={})

    result = await executor.execute(context)

    assert result == Completed(artifacts=[TextArtifact(text="")])
