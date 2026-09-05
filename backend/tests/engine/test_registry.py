from __future__ import annotations

import pytest

from app.domain.ports import NodeType
from app.engine.executor import Completed, StepContext, StepExecutor, StepResult
from app.engine.registry import StepRegistry, UnknownStepTypeError


class FakeExecutor(StepExecutor):
    def __init__(self, node_type: str) -> None:
        self._descriptor = NodeType(type=node_type, label=node_type, category="test")

    @property
    def descriptor(self) -> NodeType:
        return self._descriptor

    async def execute(self, context: StepContext) -> StepResult:
        return Completed(artifacts=[])


def test_get_returns_the_registered_executor() -> None:
    executor = FakeExecutor("noop")
    registry = StepRegistry((executor,))

    assert registry.get("noop") is executor


def test_get_raises_for_unknown_step_type() -> None:
    registry = StepRegistry(())

    with pytest.raises(UnknownStepTypeError):
        registry.get("does_not_exist")


def test_node_types_exposes_every_descriptor() -> None:
    registry = StepRegistry((FakeExecutor("a"), FakeExecutor("b")))

    assert set(registry.node_types()) == {"a", "b"}
