from __future__ import annotations

from app.domain.graph import GraphViolation


class DomainError(Exception):
    code = "domain_error"


class WorkflowValidationError(DomainError):
    code = "workflow_validation_failed"

    def __init__(self, violations: list[GraphViolation]) -> None:
        self.violations = violations
        super().__init__(f"workflow graph is invalid: {len(violations)} violation(s)")


class WorkflowNotFoundError(DomainError):
    code = "workflow_not_found"

    def __init__(self, workflow_id: object) -> None:
        self.workflow_id = workflow_id
        super().__init__(f"workflow {workflow_id} not found")


class NoWorkflowVersionError(DomainError):
    code = "no_workflow_version"

    def __init__(self, workflow_id: object) -> None:
        self.workflow_id = workflow_id
        super().__init__(f"workflow {workflow_id} has no saved version to run")


class RunNotFoundError(DomainError):
    code = "run_not_found"

    def __init__(self, run_id: object) -> None:
        self.run_id = run_id
        super().__init__(f"run {run_id} not found")
