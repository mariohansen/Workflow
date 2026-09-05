from __future__ import annotations

from app.engine.registry import StepRegistry
from app.steps.output import OutputStepExecutor
from app.steps.text_input import TextInputStepExecutor


def build_step_registry() -> StepRegistry:
    return StepRegistry((TextInputStepExecutor(), OutputStepExecutor()))
